from __future__ import annotations

import csv
import random

from collections import defaultdict
from datetime import datetime
from faker import Faker


def generate_submission_files(
        num_submissions: int,
        *,
        submission_file_path: str = "submission.csv",
        submission_topic_file_path: str = "submission_topic.csv",
        author_file_path: str = "author.csv",
        topic_list: list = None):
    """Generates sample files related to the submissions. Specifically, the submission, the
    submission topic and the author files are generated. The format of the files follows that of
    EasyChair. The EasyChair format has been inferred from actual files, there is thus no guarantees
    her that the format is exactly correct.

    Parameters
    ----------
        num_submissions: int
            The number of submission to generate.
        submission_file_path: str
            The path to the submission file that will be generated.
        submission_topic_file_path: str
            The path to the submission_topic file that will be generated.
        author_file_path: str
            The path to the author file that will be generated.
        topic_list: list
            A list of topics to chose from for the topics of the submissions.
    """

    fake = Faker()

    if topic_list is None:
        topic_list = [f"topic_{x}" for x in range(30)]

    submissions = []
    sub_to_authors = defaultdict(list)
    all_authors = dict()
    sub_to_topics = {}
    for sub_id in range(1, num_submissions + 2):
        num_authors = random.randint(1, 5)
        authors = [fake.name() for _ in range(num_authors)]
        sub_to_authors[sub_id] = authors
        for author in authors:
            all_authors[author] = None
        sub_to_topics[sub_id] = random.sample(topic_list, random.randint(2, 5))
        decision = random.choice(
            ["no decision"] * 10 + ["desk reject"] * 3 + ["reject"] * 25 + ["accept"] * 10 +
            ["withdrawn"] * 1
        )
        submission_dict = {
            "#": sub_id,
            "title": fake.sentence(nb_words=6)[:-1],
            "authors": authors,
            "submitted": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "last updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "form fields": "",
            "keywords": fake.words(nb=random.randint(2, 5)),
            "decision": decision,
            "notified": "no",
            "reviews sent": "no",
            "abstract": fake.text(max_nb_chars=500),
            "deleted?": 'yes' if random.random() < 0.05 else 'no'
        }
        submissions.append(submission_dict)

    submission_headers = [
        "#",
        "title",
        "authors",
        "submitted",
        "last updated",
        "form fields",
        "keywords",
        "decision",
        "notified",
        "reviews sent",
        "abstract",
        "deleted?"
    ]
    with open(submission_file_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(submission_headers)
        for s in submissions:
            writer.writerow([s[h] for h in submission_headers])

    author_headers = ["submission #", "first name", "last name", "email", "country", "affiliation",
                      "Web page", "person #", "corresponding?"]

    for author_id, author in enumerate(all_authors):
        all_authors[author] = {
            "first name": author.split(" ")[0],
            "last name": author.split(" ")[1],
            "email": fake.email(),
            "country": fake.country(),
            "affiliation": fake.sentence(nb_words=4)[:-1],
            "Web page": fake.url(),
            "person #": author_id + 1
        }

    with open(author_file_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(author_headers)
        for sub_id, authors in sub_to_authors.items():
            corresponding_author = random.choice(authors)
            for author in authors:
                author_details = all_authors[author]
                writer.writerow([
                    sub_id,
                    author_details["first name"],
                    author_details["last name"],
                    author_details["email"],
                    author_details["country"],
                    author_details["affiliation"],
                    author_details["Web page"],
                    author_details["person #"],
                    "yes" if author == corresponding_author else "no"
                ])

    with open(submission_topic_file_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(["submission #", "topic"])
        for sub_id, topics in sub_to_topics.items():
            for topic in topics:
                writer.writerow([sub_id, topic])


def generate_committee_files(
        committee_size: int,
        authors_file_path: str,
        *,
        committee_file_path: str = "committee.csv",
        committee_topic_file_path: str = "committee_topic.csv",
        topic_list: list = None
):
    """Generates sample files related to the committee. Specifically, the committee and the
    committee topic files are generated. The format of the files follows that of
    EasyChair. The EasyChair format has been inferred from actual files, there is thus no guarantees
    her that the format is exactly correct.

    Parameters
    ----------
        committee_size: int
            The number of persons to generate.
        authors_file_path: str
            The path to the author file as exported from EasyChair, or as generated by the function
            generate_submission_files. This is used to include some authors as reviewers.
        committee_file_path: str
            The path to the committee file that will be generated.
        committee_topic_file_path: str
            The path to the committee_topic file that will be generated.
        topic_list: list
            A list of topics to chose from for the topics of the committee members.
    """
    fake = Faker()

    if topic_list is None:
        topic_list = [f"topic_{x}" for x in range(30)]

    with open(authors_file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        all_authors = list(reader)[1:]
    max_person_id = max((int(a["person #"]) for a in all_authors), default=0)

    all_persons = []
    person_to_topics = {}
    for person_idx in range(1, committee_size + 2):
        if random.random() < 0.35:
            person_details = random.choice(all_authors)
        else:
            name = fake.name()
            person_details = {
                "#": person_idx,
                "first name": name.split(" ")[0],
                "last name": name.split(" ")[1],
                "email": fake.email(),
                "country": fake.country(),
                "affiliation": fake.sentence(nb_words=4)[:-1],
                "Web page": fake.url(),
                "person #": max_person_id + 1,
            }
            max_person_id += 1

        person_details["#"] = person_idx
        person_details["role"] = random.choice(
            ["PC member"] * 5 * 5 + ["senior PC member"] * 5 + ["associate chair"])
        all_persons.append(person_details)

        key = (
            person_details["#"], person_details["first name"] + " " + person_details["last name"])
        person_to_topics[key] = random.sample(topic_list, random.randint(5, 10))

    committee_headers = ["#", "person #", "first name", "last name", "email", "country",
                         "affiliation", "Web page", "role"]

    with open(committee_file_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(committee_headers)
        for person in all_persons:
            writer.writerow([
                person["#"],
                person["person #"],
                person["first name"],
                person["last name"],
                person["email"],
                person["country"],
                person["affiliation"],
                person["Web page"],
                person["role"]
            ])

    with open(committee_topic_file_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(["member #", "member name", "topic"])
        for person_key, topics in person_to_topics.items():
            for topic in topics:
                writer.writerow([person_key[0], person_key[1], topic])


def generate_review_files(
        submission_file_path: str,
        committee_file_path: str,
        bidding_file_path: str = "bidding.csv",
        review_file_path: str = "review.csv",
):
    """Generates sample files related to the reviews. Specifically, the bidding and the review
    files are generated. The format of the files follows that of EasyChair. The EasyChair format
    has been inferred from actual files, there is thus no guarantees her that the format is
    exactly correct.

    Parameters
    ----------
        submission_file_path: str
            The path to the submission file as exported from EasyChair, or as generated by the
            function generate_submission_files. Reviews for the submissions are generated.
        committee_file_path: str
            The path to the committee file as exported from EasyChair, or as generated by the
            function generate_committee_files. The reviewers are taken from this file.
        bidding_file_path: str
            The path to the bidding file that will be generated.
        review_file_path: str
            The path to the review file that will be generated.
    """
    fake = Faker()

    with open(submission_file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        all_submissions = list(reader)[1:]

    with open(committee_file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        all_persons = list(reader)[1:]

    person_to_bids = {}
    for person in all_persons:
        bid_dict = {}
        threshold = 20 / len(all_submissions)
        if person["role"] == "senior PC member":
            threshold *= 2.5
        if person["role"] == "associate chair":
            threshold *= 4
        for submission in all_submissions:
            if random.random() < 20 / len(all_submissions):
                if random.random() < 0.5 or person["role"] == "associate chair":
                    bid_dict[submission["#"]] = "yes"
                else:
                    bid_dict[submission["#"]] = "maybe"
        key = (person["#"], person["first name"] + " " + person["last name"])
        person_to_bids[key] = bid_dict

    with open(bidding_file_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(["member #", "member name", "submission #", "bid"])
        for person_key, bid_dict in person_to_bids.items():
            for sub, bid in bid_dict.items():
                writer.writerow([
                    person_key[0],
                    person_key[1],
                    sub,
                    bid
                ])

    all_reviews = []
    potential_reviewers = [p for p in all_persons if p["role"] == "PC member"]
    review_counter = 1
    for submission in all_submissions:
        num_reviewers = random.choice([0] + [1] * 2 + [2] * 3 + [4] * 4)
        for reviewer_idx, reviewer in enumerate(random.sample(potential_reviewers, num_reviewers)):
            score = random.randint(1, 10)
            review = {
                "#": review_counter,
                "submission #": submission["#"],
                "member #": reviewer["#"],
                "member name": reviewer["first name"] + " " + reviewer["last name"],
                "number": reviewer_idx,
                "version": random.randint(1, 5),
                "text": fake.text(2000),
                "scores": f"Score: {score}\nConfidence: {random.randint(1, 5)}",
                "total score": score,
                "reviewer first name": "",
                "reviewer last name": "",
                "reviewer email": "",
                "reviewer person #": "",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M"),
                "attachment?": "no",
            }
            if random.random() < 0.05:
                sub_reviewer = random.choice(all_persons)
                while sub_reviewer != reviewer:
                    sub_reviewer = random.choice(all_persons)
                review["reviewer first name"] = sub_reviewer["first name"]
                review["reviewer last name"] = sub_reviewer["last name"]
                review["reviewer email"] = sub_reviewer["email"]
                review["reviewer person #"] = sub_reviewer["person #"]

            all_reviews.append(review)
            review_counter += 1

    review_headers = ["#", "submission #", "member #", "member name", "number", "version", "text",
                      "scores", "total score", "reviewer first name", "reviewer last name",
                      "reviewer email", "reviewer person #", "date", "time", "attachment?"]

    with open(review_file_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(review_headers)
        for review in all_reviews:
            writer.writerow([review[h] for h in review_headers])


def generate_full_conference(
        num_submissions,
        committee_size,
        *,
        submission_file_path: str = "submission.csv",
        submission_topic_file_path: str = "submission_topic.csv",
        author_file_path: str = "author.csv",
        committee_file_path="committee.csv",
        committee_topic_file_path="committee_topic.csv",
        bidding_file_path="bidding.csv",
        review_file_path="review.csv",
        topic_list=None,
):
    """Generates sample files to simulate a full conference. The format of the files follows that of
    EasyChair. The EasyChair format has been inferred from actual files, there is thus no guarantees
    her that the format is exactly correct.

    Parameters
    ----------
        num_submissions: int
            The number of submission to generate.
        committee_size: int
            The number of persons to generate.
        submission_file_path: str
            The path to the submission file that will be generated.
        submission_topic_file_path: str
            The path to the submission_topic file that will be generated.
        author_file_path: str
            The path to the author file that will be generated.
        committee_file_path: str
            The path to the committee file that will be generated.
        committee_topic_file_path: str
            The path to the committee_topic file that will be generated.
        topic_list: list
            A list of topics to chose from for the topics of the submissions and of the committee
            members.
        bidding_file_path: str
            The path to the bidding file that will be generated.
        review_file_path: str
            The path to the review file that will be generated.
    """
    generate_submission_files(
        num_submissions,
        submission_file_path=submission_file_path,
        author_file_path=author_file_path,
        submission_topic_file_path=submission_topic_file_path,
        topic_list=topic_list,
    )

    generate_committee_files(
        committee_size,
        author_file_path,
        committee_file_path=committee_file_path,
        committee_topic_file_path=committee_topic_file_path,
        topic_list=topic_list,
    )

    generate_review_files(
        submission_file_path,
        committee_file_path,
        bidding_file_path=bidding_file_path,
        review_file_path=review_file_path
    )


# if __name__ == "__main__":
#     import os
#
#     from easychair_extra.read import read_topics
#
#     areas_to_topics, topics_to_areas = read_topics(
#         os.path.join("..", "easychair_sample_files", "topics.csv")
#     )
#     generate_full_conference(
#         1000,
#         2800,
#         submission_file_path=os.path.join("..", "easychair_sample_files", "submission.csv"),
#         submission_topic_file_path=os.path.join("..", "easychair_sample_files",
#                                                 "submission_topic.csv"),
#         author_file_path=os.path.join("..", "easychair_sample_files", "author.csv"),
#         committee_file_path=os.path.join("..", "easychair_sample_files", "committee.csv"),
#         committee_topic_file_path=os.path.join("..", "easychair_sample_files",
#                                                "committee_topic.csv"),
#         bidding_file_path=os.path.join("..", "easychair_sample_files", "bidding.csv"),
#         review_file_path=os.path.join("..", "easychair_sample_files", "review.csv"),
#         topic_list=list(topics_to_areas)
#     )
