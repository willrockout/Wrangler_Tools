
from ingest.api.ingestapi import IngestApi
from ingest.importer.importer import XlsImporter
import os
import argparse
import re


class GraphValidator:
    def __init__(self, file):
        ingest_url = os.environ.get('INGEST_API', 'https://api.ingest.data.humancellatlas.org')
        ingest_api = IngestApi(url=ingest_url)
        self.importer = XlsImporter(ingest_api)
        self.entity_map = self.importer.dry_run_import_file(file)
        self.node_by_type = self.entity_map.entities_dict_by_type
        self.links = {}
        self.files = []
        self.donors = []
        self.path_dict = {}
        self.process_prot_link = {}
        self.high_level = {}
        self.known_position = ["donor_organism", "library_preparation_protocol", "sequencing_protocol"]
        self.unknown_position = ["specimen_from_organism", "cell_line", "organoid", "collection_protocol",
                                 "enrichment_protocol", "dissociation_protocol", "cell_suspension"]
        self.high_level_paths = []

    def get_all_links(self):
        order_list = ['file', 'biomaterial', 'process']
        for order in order_list:
            for uniq_node, val in self.node_by_type[order].items():
                process = False
                if order == 'file':
                    self.files.append(uniq_node)
                if order == 'biomaterial':
                    if self.node_by_type.get(order)[uniq_node].content.get('describedBy').split('/')[-1:][0] == 'donor_organism':
                        self.donors.append(uniq_node)
                direct_links = val.direct_links
                if direct_links:
                    for link in direct_links:
                        direct_link_id = link.get('id')
                        if link.get('entity') == 'process':
                            process = True
                            if uniq_node not in self.links.keys():
                                self.links[uniq_node] = []
                                self.links[uniq_node].append(direct_link_id)
                            else:
                                self.links[uniq_node].append(direct_link_id)
                        if order == 'process':
                            if link.get('entity') == 'protocol':
                                if uniq_node not in self.process_prot_link.keys():
                                    self.process_prot_link[uniq_node] = []
                                    self.process_prot_link[uniq_node].append(link.get('id'))
                                else:
                                    if link.get('id') not in self.process_prot_link[uniq_node]:
                                        self.process_prot_link[uniq_node].append(link.get('id'))
                if not process:
                    self.links[uniq_node] = []

    def add_process_links(self):
        for key, val in self.links.items():
            for link in val:
                if link in self.links.keys():
                    if key not in self.links[link]:
                        self.links[link].append(key)

    def identify_float(self):
        for key in self.links.keys():
            if not self.links[key]:
                print('%s is a floating entity' % key)

    def find_path(self, s, e, link_graph, path=None):
        if not path:
            path = []
        path = path + [s]
        # print(path)
        if s == e:
            return path
        if s not in link_graph:
            return None
        for node in link_graph[s]:
            if node not in path:
                extended_path = self.find_path(node, e, link_graph, path=path)

                if extended_path:
                    return extended_path
        return None

    def find_all_paths(self):
        for f in self.files:
            for d in self.donors:
                entity_full_path = self.find_path(f, d, self.links)
                if entity_full_path:
                    filename = entity_full_path[0]
                    entity_path = entity_full_path[1:]
                    for key in self.process_prot_link:
                        if key in entity_path:
                            entity_path[entity_path.index(key)] = key + '/' + '/'.join(self.process_prot_link[key])
                    entity_path.reverse()
                    entity_path = ':'.join(entity_path)
                    if entity_path not in self.path_dict.keys():
                        self.path_dict[entity_path] = []
                        self.path_dict[entity_path].append(filename)
                    else:
                        self.path_dict[entity_path].append(filename)

    def clean_output(self):
        for key, val in self.path_dict.items():
            print('%s %s' % (key.replace(':', ' -> '), val))

    def gather_entity_info(self):
        for node_type in self.node_by_type:
            node_dict = self.node_by_type.get(node_type)
            for uniq_node, val in node_dict.items():
                specific_type = val.content.get('describedBy').split('/')[-1:][0]
                if specific_type not in self.high_level:
                    self.high_level[specific_type] = []
                    if uniq_node not in self.high_level[specific_type]:
                        self.high_level[specific_type].append(uniq_node)
                else:
                    self.high_level[specific_type].append(uniq_node)

    def summary(self):
        print('Number of bundles: %s' % len(self.path_dict.keys()))
        for key, val in self.high_level.items():
            print('Number of %s: %s' % (key, len(val)))

    # def build_high_level_graphs(self):
    #     for entities, files in self.path_dict.item():
    #         high_level_path = []
    #         for entity in entities.split(':'):
    #             if entities.split(':').index(entity) == 0:
    #                 if entity in self.high_level['donor_organism']:
    #                     high_level_path.append('donor_organism')
    #             elif re.search("-", entity):
    #                 for protocol in entity.split("/")[1:]:
    #                     if protocol in
    #


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This script provided a number of different "
                                                 "tools to obtain graph information from a spreadsheet")
    parser.add_argument('--input_file', '-i', help='Input excel spreadsheet')
    parser.add_argument('--summary', '-sum', action='store_true', help='Summary of spreadsheet')
    parser.add_argument('--stdout', '-sto', action='store_true', help='Output full paths')
    args = parser.parse_args()

    pathFinder = GraphValidator(args.input_file)

    pathFinder.get_all_links()
    pathFinder.add_process_links()
    pathFinder.identify_float()
    pathFinder.find_all_paths()
    # print(pathFinder.path_dict.items())

    if args.summary:
        pathFinder.gather_entity_info()
        pathFinder.summary()
    elif args.stdout:
        pathFinder.clean_output()
