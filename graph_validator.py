
from ingest.api.ingestapi import IngestApi
from ingest.importer.importer import XlsImporter
import os
import argparse


class GraphValidator():
    def __init__(self):
        ingest_url = os.environ.get('INGEST_API', 'https://api.ingest.data.humancellatlas.org')
        ingest_api = IngestApi(url=ingest_url)
        self.importer = XlsImporter(ingest_api)
        self.links = {}
        self.files = []
        self.donors = []
        self.path_dict = {}

    def get_all_links(self, file):
        order_list = ['file', 'biomaterial', 'process']
        entity_map = self.importer.dry_run_import_file(file)
        node_by_type = entity_map.entities_dict_by_type
        for order in order_list:
            for uniq_node, val in node_by_type[order].items():
                process = False
                if order == 'file':
                    self.files.append(uniq_node)
                if order == 'biomaterial':
                    if node_by_type.get(order)[uniq_node].content.get('describedBy').split('/')[-1:][0] == 'donor_organism':
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
                if not process:
                    self.links[uniq_node] = []

    def add_process_links(self):
        for key, val in self.links.items():
            for link in val:
                if link in self.links.keys():
                    if key not in self.links[link]:
                        self.links[link].append(key)

    def find_path(self, s, e, link_graph, path=None):
        if not path:
            path = []
        path = path + [s]
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
                    entity_path.reverse()
                    entity_path = ':'.join(entity_path)
                    if entity_path not in self.path_dict.keys():
                        self.path_dict[entity_path] = []
                        self.path_dict[entity_path].append(filename)
                    else:
                        self.path_dict[entity_path].append(filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This script provided a number of different tools to obtain graph information from a spreadsheet")
    parser.add_argument('--input_file', '-i', help='Input excel spreadsheet')
    args = parser.parse_args()

    pathFinder = GraphValidator()

    pathFinder.get_all_links(args.input_file)
    pathFinder.add_process_links()
    pathFinder.find_all_paths()
    print(pathFinder.path_dict)
