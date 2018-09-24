"""
Run this to prepare JSON of ID occurrences and probabilities using .traffic file
"""

import os
import json
from matplotlib.backends.backend_pdf import PdfPages

from NNIDS.parsers import traffic
import NNIDS.plotters.plotter as plotter

wd = os.getcwd()
files = [wd + '/data/traffic/local_Aug_31.traffic']
# files = [wd + '/data/traffic/asia_train.traffic']


def id_occurrence_analyzer(file_data_map):
    """
    Analyze the contents of each file in file_data_map and combines the results.
    Obtains the number of occurrences of each ID and the probability of its occurrence
    across the files.
    Write the results to 'data/traffic_analysis_dump/id_occurrences.json'.

    :param file_data_map: dict of file names and list of CANMessage objects
    :return: None
    """
    all_id_freq_map = {}
    for file in file_data_map:
        for can_msg in file_data_map[file]:
            if can_msg.id not in all_id_freq_map:
                all_id_freq_map[can_msg.id] = {}
                all_id_freq_map[can_msg.id]['Occurrences'] = 1
            else:
                all_id_freq_map[can_msg.id]['Occurrences'] \
                    = all_id_freq_map[can_msg.id]['Occurrences'] + 1

    total_msgs = 0
    for msg_id in all_id_freq_map:
        total_msgs = total_msgs + all_id_freq_map[msg_id]['Occurrences']

    for msg_id in all_id_freq_map:
        all_id_freq_map[msg_id]['Probability'] = all_id_freq_map[msg_id]['Occurrences'] \
                                                 / float(total_msgs)

    # with open('data/traffic_analysis_dump/id_occurrences.json', 'w') as json_file:
    #     json_file.write(json.dumps(all_id_freq_map, sort_keys=True, indent=4))

    with open('data/traffic_analysis_dump/id_occurrences_asia.json', 'w') as json_file:
        json_file.write(json.dumps(all_id_freq_map, sort_keys=True, indent=4))


def id_frequency_analyzer(file_data_map):
    all_data = {}
    for file in file_data_map:
        i = 0
        while i < len(file_data_map[file]) - 1:
            one_second_data = {}
            t_i = file_data_map[file][i].timestamp
            one_second_data[file_data_map[file][i].id] = 1
            i = i + 1
            if i >= len(file_data_map[file]):
                break
            t_t = file_data_map[file][i].timestamp
            while t_t <= t_i + 1000:  # milliseconds
                if file_data_map[file][i].id not in one_second_data:
                    one_second_data[file_data_map[file][i].id] = 1
                else:
                    one_second_data[file_data_map[file][i].id] \
                        = one_second_data[file_data_map[file][i].id] + 1
                i = i + 1
                if i >= len(file_data_map[file]):
                    break
                t_t = file_data_map[file][i].timestamp

            for msg_id in one_second_data:
                if msg_id not in all_data:
                    all_data[msg_id] = {}
                    all_data[msg_id][one_second_data[msg_id]] = 1
                else:
                    if one_second_data[msg_id] not in all_data[msg_id]:
                        all_data[msg_id][one_second_data[msg_id]] = 1
                    else:
                        all_data[msg_id][one_second_data[msg_id]] \
                            = all_data[msg_id][one_second_data[msg_id]] + 1

    figures = []
    for identifier in all_data:
        [fig, avg_freq] = plotter.plot_id_frequency_distribution('Frequency Distribution of ID 0x'
                                                                 + identifier,
                                                                 all_data[identifier])
        figures.append(fig)
        all_data[identifier]['Average Frequency'] = avg_freq

    pp = PdfPages('data/plots/us_id_frequency_distribution.pdf')
    for fig in figures:
        pp.savefig(fig)
    pp.close()

    # with open('data/analysis_dump/id_frequency_distribution.json', 'w') as json_file:
    #     json_file.write(json.dumps(all_data, indent=4))
    #
    # pp = PdfPages('plots/id_average_frequency.pdf')
    # fig = plotter.plot_id_avg_frequency('Average Frequency of Each CAN ID', all_data)
    # pp.savefig(fig)
    # pp.close()


if __name__ == "__main__":
    can_msgs = {}
    for file in files:
        can_msgs[file] = traffic.traffic_parser(file)

    # id_occurrence_analyzer(can_msgs)
    id_frequency_analyzer(can_msgs)
