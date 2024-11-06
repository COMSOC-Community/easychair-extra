import csv
import os.path
import random
from collections import defaultdict
from datetime import datetime

from faker import Faker

from easychair_extra.read import author_list_to_str, read_topics


def generate_submission_files(
        num_submission: int,
        *,
        submission_file_path: str = "submission.csv",
        submission_topic_file_path: str = "submission_topic.csv",
        author_file_path: str = "author.csv",
        topic_list: list = None):
    """Generates a sample "author.csv" file following the typical EasyChair format (no guarantees
     here). """

    fake = Faker()

    if topic_list is None:
        topic_list = [f"topic_{x}" for x in range(30)]

    submissions = []
    sub_to_authors = defaultdict(list)
    all_authors = dict()
    sub_to_topics = {}
    for sub_id in range(1, num_submission + 2):
        num_authors = random.randint(1, 5)
        authors = [fake.name() for _ in range(num_authors)]
        sub_to_authors[sub_id] = authors
        for author in authors:
            all_authors[author] = None
        sub_to_topics[sub_id] = random.sample(topic_list, random.randint(2, 5))
        submission_dict = {
            "#": sub_id,
            "title": fake.sentence(nb_words=6)[:-1],
            "authors": authors,
            "keywords": fake.words(nb=random.randint(2, 5)),
            "abstract": fake.text(max_nb_chars=500),
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
            writer.writerow([
                s["#"],
                s["title"],
                author_list_to_str(s["authors"]),
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                "",
                '\n'.join(s["keywords"]),
                '',
                'no',
                'no',
                s["abstract"],
                'yes' if random.random() < 0.05 else 'no'
            ])

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
        submission_file_path,
        committee_file_path,
        bidding_file_path="bidding.csv",
        review_file_path="review.csv",
):
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


if __name__ == "__main__":
    areas_to_topics, topics_to_areas = read_topics(os.path.join("..", "easychair_sample_files", "topics.csv"))
    generate_full_conference(
        500,
        1500,
        submission_file_path=os.path.join("..", "easychair_sample_files", "submission.csv"),
        submission_topic_file_path=os.path.join("..", "easychair_sample_files",
                                                "submission_topic.csv"),
        author_file_path=os.path.join("..", "easychair_sample_files", "author.csv"),
        committee_file_path=os.path.join("..", "easychair_sample_files", "committee.csv"),
        committee_topic_file_path=os.path.join("..", "easychair_sample_files",
                                               "committee_topic.csv"),
        bidding_file_path=os.path.join("..", "easychair_sample_files", "bidding.csv"),
        review_file_path=os.path.join("..", "easychair_sample_files", "review.csv"),
        topic_list=list(topics_to_areas)
    )
