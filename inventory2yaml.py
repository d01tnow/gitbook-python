#!/usr/bin/env python3
# coding: utf-8

import configparser
import yaml
from functools import reduce
from itertools import chain


class Group(yaml.YAMLObject):
    yaml_tag = '!group'

    def __init__(self, name):
        self.vars = None
        self.hosts = None
        self.children = None
        self.name = name.lower()

    def __repr__(self):
        return '%s(vars=%r, children=%r)' % (self.name, self.vars, self.hosts)

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
        self.children = {**self.children, **group}

    def merge(self, group):
        if group.name == self.name:
            self.__merge_children(group.children)
            self.__merge_hosts(group.hosts)
            self.__merge_vars(group.vars)
        else:
            self.__append_children(group)


def split_section_name(section_name):
    splitted_section = section_name.split(':')
    group_name = splitted_section[0]
    handler_tag = ('hosts' if len(splitted_section) < 2 else splitted_section[1])
    return group_name, handler_tag


def parse_host_variable(group, section_items):
    flatten_section_items = ['='.join(x) for x in section_items]
    print(group.name, ':', flatten_section_items)


def parse_children(group, section_items):
    group.children = dict(map(lambda x: (x, None), section_items))


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
    cf = configparser.ConfigParser()
    cf.read(inventory)
    print(cf.sections())
    print(cf.items('all:vars'))
    print(cf.items('mariadb'))
    return cf


def main():
    inventory = u'/data/home/cody/work/11_platform/works/02_技术开发/06_实施布署/ansible/projects/王志军/dev-inventory'
    cf = parse_inventory(inventory)
    group_creator = get_group_creator_from(cf)
    groups = list(map(group_creator, cf.sections()))
    print('---------\n')
    for g in groups:
        print(g)
    print('---------\n')
    # print(yaml.dump(groups))

    # yml_file = u'/data/home/cody/work/11_platform/works/02_技术开发/06_实施布署/ansible/projects/王志军/dev/elasticsearch.yml'
    # with open(yml_file, 'r') as f:
    #     es_yml = yaml.safe_load(f)
    # print(es_yml['all'])


if __name__ == "__main__":
    main()
