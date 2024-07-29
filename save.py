import csv
import os


def remove_file_it_exists(filepath):
    # Remove file if it exist
    try:
        os.remove(filepath)
    except OSError:
        print("OS Error")


def save(filepath, colnames, results):

    remove_file_it_exists(filepath)

    with open(filepath, "w", newline="") as csv_writer:
        writer = csv.writer(csv_writer, delimiter="\t")
        writer.writerow(colnames)
        writer.writerows(results)
