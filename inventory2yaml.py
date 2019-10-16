#!/usr/bin/env python3
# coding: utf-8

from io import StringIO
import configparser
import yaml
from functools import reduce
from itertools import chain
from enum import Enum
from enum import unique


class Group(yaml.YAMLObject):
    yaml_tag = '!group'

    def __init__(self, name):
        self.vars = None
        self.hosts = None
        self.children = None
        self.name = name.lower()

    def __repr__(self):
        return '%s(vars=%r, children=%r, hosts=%r)' % (self.name, self.vars, self.children, self.hosts)

    def __merge_vars(self, variables):
        if not self.vars:
            self.vars = variables
            return
        if variables:
            self.vars.update(variables)

    def __merge_hosts(self, hosts):
        if not self.hosts:
            self.hosts = hosts
            return
        if hosts:
            self.hosts.update(hosts)

    def __merge_children(self, children):
        if not self.children:
            self.children = children
            return
        if children:
            self.children.update(children)

    def __append_children(self, group):
        if not self.children:
            self.children = {group.name: group}
            return
        self.children = {**self.children, group.name: group}
        print('self: ', self.name, ', append group: ', group)

    def merge(self, group):
        print('merge group name: ', group.name)
        if group.name == self.name:
            self.__merge_children(group.children)
            self.__merge_hosts(group.hosts)
            self.__merge_vars(group.vars)
        else:
            if not self.children:
                self.__append_children(group)
            print('self.children:', self.children)
            if group.name in self.children:
                if self.children[group.name]:
                    self.children[group.name].merge(group)
                else:
                    self.children[group.name] = group
            else:
                moved_children = []
                for k,v in self.children.items():
                    if group.children and k in group.children:
                        group.__merge_children({k: v})
                        moved_children.append(k)
                    if self.children[k].children and group.name in self.children[k].children:
                        self.children[k].merge(group)
                if moved_children:
                    for cld in moved_children: del self.children[cld]
                    self.__merge_children({group.name: group})


        return self


def split_section_name(section_name):
    splitted_section = section_name.split(':')
    group_name = splitted_section[0]
    handler_tag = ('hosts' if len(splitted_section) < 2 else splitted_section[1])
    return group_name, handler_tag

@unique
class State(Enum):
    finding_alias = 1
    found_alias = 2
    finding_key = 3
    found_key = 4
    finding_value=5
    found_value=6
    finding_value_in_quote=7


def parse_host_variables_from_line(line):
    host = {}
    alias = ''
    key = ''
    value = ''
    state = State.finding_alias.value
    idx = 0
    for c in line:
        idx += 1
        if state == State.finding_alias.value:
            if c != ' ':
                alias += c
                if len(line) == idx:
                    host[alias] = None
                    break
            else:
                state = State.found_alias.value
                host[alias] = None
        elif state == State.found_alias.value or state == State.found_value.value:
            if c == ' ':
                continue
            else:
                state = State.finding_key.value
                key += c
        elif state == State.finding_key.value:
            if c == ' ' or c == '=':
                state = State.found_key.value
            else:
                key += c
        elif state == State.found_key.value:
            if c == '"':
                state = State.finding_value_in_quote.value
            else:
                state = State.finding_value.value
            value += c
        elif state == State.finding_value_in_quote.value:
            if c == '"':
                state = State.found_value.value
                value += c
                if host[alias] is None:
                    host[alias] = {key: value}
                else:
                    host[alias].update({key: value})
                key = ''
                value = ''
            else:
                value += c
        elif state == State.finding_value.value:
            if c == ' ':
                state = State.found_value.value
                if host[alias] is None:
                    host[alias] = {key: value}
                else:
                    host[alias].update({key: value})
                key = ''
                value = ''
            else:
                value += c
                if len(line) == idx:
                    state = State.found_value.value
                    if host[alias] is None:
                        host[alias] = {key: value}
                    else:
                        host[alias].update({key: value})
                    key = ''
                    value = ''
                    break

    return host


def handle_multi_hosts_and_port(host):
    hosts = []
    for key, value in host.items():
        host_names = key.split(':')
        if len(host_names) == 1:
            hosts = [host]
        else:

            multi_hosts_prefix_and_start = host_names[0].split('[')
            multi_hosts_prefix, start = multi_hosts_prefix_and_start[0], multi_hosts_prefix_and_start[1]
            multi_hosts_postfix_and_end = host_names[1].split(']')
            end = multi_hosts_postfix_and_end[0]
            multi_hosts_postfix = multi_hosts_postfix_and_end[1] if len(multi_hosts_postfix_and_end)>0 else ''
            values = value

            if len(host_names) == 3:
                values.update({'ansible_ssh_port': host_names[2]})
            gen_host_name = lambda x: '%s%s%s' % (multi_hosts_prefix, x, multi_hosts_postfix)
            key_host_names = [ gen_host_name(chr(ord(start)+i)) for i in range(ord(end) - ord(start)+1)]
            hosts = [ {k: values} for k in key_host_names ]

    return hosts


def parse_host_variable(group, section_items):
    flatten_section_items = []
    # 处理以下情况
    # g2:  [('192.168.39.2[1', '5]1:3333 ansible_user="user" var_g2_1=2222'), ('192.168.39.30 ansible_user', '"user30" var_g2_2=3333')]
    if '[' in section_items[0][0]:
        flatten_section_items = [':'.join(section_items[0])] + ['='.join(x) for x in section_items[1:] ]
    else:
        flatten_section_items = ['='.join(x) for x in section_items]
    for line in flatten_section_items:
        host = parse_host_variables_from_line(line)
        hosts = handle_multi_hosts_and_port(host)
        if not group.hosts:
            group.hosts = {}
        for g in hosts:
            group.hosts.update(g)


def parse_children(group, section_items):
    group.children = dict(section_items)


def parse_group_variable(group, section_items):
    group.vars = dict(section_items)


section_parser = {
    'hosts': parse_host_variable,
    'vars': parse_group_variable,
    'children': parse_children
    }


def get_group_creator_from(config_parser):
    def gen_group(section_name):
        section = split_section_name(section_name)
        g = Group(section[0])
        section_parser[section[1]](g, config_parser.items(section_name))
        return g

    return gen_group


def parse_inventory(inventory):
    cf = configparser.RawConfigParser(allow_no_value=True)
    cf.read_file(StringIO(inventory))
    print(cf.sections())
    print('all:vars: ', cf.items('all:vars'))
    print('g1: ', cf.items('g1'))
    print('g2: ', cf.items('g2'))
    print('gg1:children - ', cf.items('gg1:children'))
    return cf


test_inventory = '''
[all:vars]
ansible_user=test_user

[g1]
alias1_1 ansible_host=192.168.39.1 var1_1=22
alias1_2 ansible_host=192.168.39.2 var1_2="hi, all"

[g1:vars]
ansible_ssh_port=2222

[gg1:children]
g1
g2

[g2]
192.168.39.2[1:5]1:3333 ansible_user="user" var_g2_1=2222
192.168.39.30 ansible_user="user30" var_g2_2=3333
[g2:vars]
g2_var=123


'''
def main():
    #inventory = u'/data/home/cody/work/11_platform/works/02_技术开发/06_实施布署/ansible/projects/王志军/dev-inventory'
    cf = parse_inventory(test_inventory)
    group_creator = get_group_creator_from(cf)
    groups = list(map(group_creator, cf.sections()))
    print('---------\n')
    group_all = reduce(lambda s, x: s.merge(x), groups, Group('all'))
    for g in groups:
        print(g)
    print('---------\n')
    # print(group_all)
    print(yaml.dump(group_all))
    with open('./invtory.yml', 'w+', encoding='utf-8') as fw:
        yaml.dump(group_all, fw)

    # yml_file = u'/data/home/cody/work/11_platform/works/02_技术开发/06_实施布署/ansible/projects/王志军/dev/elasticsearch.yml'
    # with open(yml_file, 'r') as f:
    #     es_yml = yaml.safe_load(f)
    # print(es_yml['all'])


if __name__ == "__main__":
    main()
