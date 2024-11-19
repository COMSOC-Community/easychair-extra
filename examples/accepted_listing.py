# Extract list of accepted papers from EasyChair submission file
# Ulle Endriss, 4 July 2024

import csv
import os

from easychair_extra.read import read_submission, read_author


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.join(current_dir, "..", "easychair_sample_files")

    # read submission and author files
    submissions = read_submission(
        os.path.join(root_dir, "submission.csv"),
        author_file_path=os.path.join(root_dir, "author.csv")
    )
    accepted_submissions = submissions[submissions["decision"] == "accept"]

    authors = read_author(os.path.join(root_dir, "author.csv"))

    # prefix for submission numbers (M for main track, D for demo track, etc.)
    prefix = 'M'
    papers_details = []
    accepted_papers_ids = set()

    def populate_papers_details(df_row):
        key = f"{prefix}{df_row['#']}"
        accepted_papers_ids.add(key)
        papers_details.append({
            "paper": key,
            "title": df_row["title"],
            "authors": df_row["authors"],
        })

    accepted_submissions.apply(populate_papers_details, axis=1)
    papers_details.sort(key=lambda x: x["paper"])

    author_details = []

    def populate_authors_details(df_row):
        for sub_id in df_row["submission_ids"]:
            key = f"{prefix}{sub_id}"
            if key in accepted_papers_ids:
                author_details.append({
                    "paper": key,
                    "author": df_row["full name"],
                    "email": df_row["email"],
                })

    authors.apply(populate_authors_details, axis=1)
    author_details.sort(key=lambda x: x["paper"])

    # path to output paper file
    # headers: paper, author, email
    if len(papers_details) > 0:
        accepted_papers_csv = 'accepted_papers_main_track.csv'
        with open(accepted_papers_csv, 'w', newline='', encoding='utf-8') as file:
            fieldnames = papers_details[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(papers_details)

    if len(author_details) > 0:
        accepted_authors_csv = 'accepted_authors_main_track.csv'
        with open(accepted_authors_csv, 'w', newline='', encoding='utf-8') as file:
            fieldnames = author_details[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(author_details)


if __name__ == "__main__":
    main()
