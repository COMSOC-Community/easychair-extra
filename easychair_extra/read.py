import csv

import pandas as pd


def authors_as_list(authors: str):
    """Transforms a string of authors of the type "author1, author2 and author3" into a list
    ["author1", "author2", "author3"].

    Parameters
    ----------
        authors: str
            A string of author names
    """
    and_split = authors.split(" and ")
    if len(and_split) == 2:
        last_author = and_split[1].strip()
        authors = and_split[0]
    elif len(and_split) == 1:
        last_author = None
        authors = and_split[0]
    else:
        raise ValueError("The and split returned more than 2 values")
    res = [a.strip() for a in authors.split(",") if a.strip()]
    if last_author:
        res.append(last_author)
    return res


def author_list_to_str(authors: list):
    """Transforms a list of authors of the type ["author1", "author2", "author3"] into a string
    "author1, author2 and author3".

    Parameters
    ----------
        authors: list
            A list of author names
    """
    if len(authors) == 1:
        return str(authors[0])
    last_author = authors[-1]
    res = ', '.join(authors[:-1])
    res += " and " + str(last_author)
    return res


def read_topics(topic_file_path: str):
    """Reads the topic file and return two dictionaries: a mapping from areas to lists of topics and
    the reverse mapping from topics to areas.

    Parameters
    ----------
        topic_file_path: str
            Path to the file to read the topics
    """
    area_topics = {}
    topics_area = {}
    with open(topic_file_path) as f:
        reader = csv.DictReader(f)
        current_area = ""
        current_topics = []
        for row in reader:
            topic = row["topic"]
            if row["header?"] == "yes":
                if current_topics:
                    area_topics[current_area] = current_topics
                current_area = topic
                current_topics = []
            else:
                current_topics.append(topic)
                topics_area[topic] = current_area
        area_topics[current_area] = current_topics
    return area_topics, topics_area


def read_committee(
    committee_file_path,
    *,
    committee_topic_file_path=None,
    topics_to_areas=None,
    bids_file_path=None,
):
    """Reads the committee file and return a dataframe with its content.

    If the arguments committee_topic_file_path and topics_to_areas are provided, the topics
    selected by committee members are added to the dataframe.

    If the argument bids_file_path is provided, the bids submitted by the committee members are
    added to the dataframe.

    Parameters
    ----------
        committee_file_path: str
            Path to the file to read for the committee
        committee_topic_file_path: str
            Path to the file to read the topics for the members of the committee
        topics_to_areas: dict
            Dictionary mapping topics to areas to map papers to areas
        bids_file_path: str
            Path to the file to read the bids submitted by the committee
    """
    df = pd.read_csv(committee_file_path, delimiter=",", encoding="utf-8")
    df["person #"] = pd.to_numeric(df["person #"], downcast="integer")
    df["full name"] = df["first name"] + " " + df["last name"]

    if committee_topic_file_path:
        if not topics_to_areas:
            raise ValueError(
                "If you set the committee_topic_file_path, then you also need to "
                "provide the topics_to_areas mapping."
            )
        pc_to_topics = {}
        pc_to_areas = {}
        with open(committee_topic_file_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                topic = row["topic"]  # The topic
                member_id = int(row["member #"].strip())  # The id of the PC member
                if member_id in pc_to_topics:
                    pc_to_topics[member_id].append(topic)
                else:
                    pc_to_topics[member_id] = [topic]
                area = topics_to_areas[topic]
                if member_id in pc_to_areas and area not in pc_to_areas[member_id]:
                    pc_to_areas[member_id].append(area)
                else:
                    pc_to_areas[member_id] = [area]
        df["topics"] = df.apply(
            lambda df_row: pc_to_topics.get(df_row["#"], []), axis=1
        )
        df["areas"] = df.apply(lambda df_row: pc_to_areas.get(df_row["#"], []), axis=1)

    if bids_file_path:
        pc_to_bids = {}
        bid_levels = set()
        with open(bids_file_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                member_id = int(row["member #"])
                submission = int(row["submission #"])
                bid = row["bid"]
                bid_levels.add(bid.strip().replace(" ", "_"))
                if member_id in pc_to_bids:
                    if bid in pc_to_bids[member_id]:
                        pc_to_bids[member_id][bid].append(submission)
                    else:
                        pc_to_bids[member_id][bid] = [submission]
                else:
                    pc_to_bids[member_id] = {bid: [submission]}

        def find_bids(df_row, bid_level):
            bids_dict = pc_to_bids.get(df_row["#"], None)
            if bids_dict is not None:
                return bids_dict.get(bid_level, [])
            return []

        for bid in bid_levels:
            df["bids_" + bid] = df.apply(lambda df_row: find_bids(df_row, bid), axis=1)

    return df


def read_submission(
    submission_file_path: str,
    *,
    submission_topic_file_path: str = None,
    author_file_path: str = None,
    review_file_path: str = None,
    submission_field_value_path: str = None,
    topics_to_areas: dict = None,
    remove_deleted: bool = True,
    remove_desk_reject: bool = True,
):
    """Reads the submission file and return a dataframe with its content.

    If the argument submission_topic_file_path is provided, the topics assigned to the submissions
    are added to the dataframe. In case topics_to_areas is also provided, then the areas
    corresponding to the topics are also added to the dataframe.

    If the argument author_file_path is provided, the ids of the authors of the submission are added
    to the dataframe.

    If the argument review_file_path is provided, the total score of the submission in the review
    process is added to the dataframe.

    If the argument submission_field_value_path is provided, the field "student-paper" is looked
    for in order to assess all authors of a submission are students.

    Parameters
    ----------
        submission_file_path: str
            Path to the file to read for the submissions
        submission_topic_file_path: str
            Path to the file to read the topics for the submissions
        author_file_path: str
            Path to the file to read the details of the authors of the submissions
        review_file_path: str
            Path to the file to read the reviews submitted for the submissions
        submission_field_value_path: str
            Path to the file to read for additional fields about the submissions
        topics_to_areas: dict
            Dictionary mapping topics to areas to map papers to areas
        remove_deleted: bool
            If True, the submissions with deleted? = "yes" are removed
        remove_desk_reject: bool
            If True, the submissions with decision = "desk reject" are removed
    """
    df = pd.read_csv(submission_file_path, delimiter=",", encoding="utf-8")
    if remove_deleted:
        df.drop(df[df["deleted?"] == "yes"].index, inplace=True)
    if remove_desk_reject:
        df.drop(df[df["decision"] == "desk reject"].index, inplace=True)

    if submission_topic_file_path:
        sub_to_topics = {}
        sub_to_areas = {}
        with open(submission_topic_file_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                topic = row["topic"]  # The topic
                sub_id = int(row["submission #"].strip())  # The id of the submission
                if sub_id in sub_to_topics:
                    sub_to_topics[sub_id].append(topic)
                else:
                    sub_to_topics[sub_id] = [topic]
                if topics_to_areas:
                    area = topics_to_areas[topic]
                    if sub_id in sub_to_areas and area not in sub_to_areas[sub_id]:
                        sub_to_areas[sub_id].append(area)
                    else:
                        sub_to_areas[sub_id] = [area]
        df["topics"] = df.apply(
            lambda df_row: sub_to_topics.get(df_row["#"], []), axis=1
        )
        if topics_to_areas:
            df["areas"] = df.apply(
                lambda df_row: sub_to_areas.get(df_row["#"], []), axis=1
            )

    if author_file_path:
        sub_to_authors = {}
        with open(author_file_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sub_id = int(row["submission #"].strip())  # The id of the submission
                person_id = int(row["person #"].strip())  # The id of the person in EC
                if sub_id in sub_to_authors:
                    sub_to_authors[sub_id].append(person_id)
                else:
                    sub_to_authors[sub_id] = [person_id]
        df["authors_id"] = df.apply(
            lambda df_row: sub_to_authors.get(df_row["#"], []), axis=1
        )

    if submission_field_value_path:
        sub_to_is_students = {}
        with open(submission_field_value_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sub_id = int(row["submission #"].strip())  # The id of the submission
                field_name = row["field name"]
                if field_name == "student-paper":
                    sub_to_is_students[sub_id] = row["value"] == "allstudent"
        df["all_authors_students"] = df.apply(
            lambda df_row: sub_to_is_students.get(df_row["#"], False), axis=1
        )

    if review_file_path:
        sub_to_total_scores = {}
        with open(review_file_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sub_id = int(row["submission #"].strip())
                total_score = int(row["total score"].strip())
                if sub_id in sub_to_total_scores:
                    sub_to_total_scores[sub_id].append(total_score)
                else:
                    sub_to_total_scores[sub_id] = [total_score]
        df["total_scores"] = df.apply(
            lambda df_row: sub_to_total_scores.get(df_row["#"], []), axis=1
        )
    return df
