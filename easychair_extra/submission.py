from __future__ import annotations

from pandas import DataFrame


def bid_similarity(
    submission_df: DataFrame, committee_df: DataFrame, bid_level_weight: dict
):
    """Returns a dictionary mapping submission identifiers to a bid similarity dict. The latter is a
    dictionary mapping submissions to their bid similarity score.

    The bid similarity score between s1 and s2 is the number of reviewers who submitted a
    positively-weighted bid for s1 and s2, divided by the number of reviewers who submitted a
    positively-weighted bid for either s1 or s2 (the Jaccard distance between sets of reviewers).

    Parameters
    ----------
        submission_df : pandas.DataFrame
            The submission dataframe
        committee_df : pandas.DataFrame
            The committee dataframe
        bid_level_weight : dict
            A dict indicating for each bid level a weight.
    """
    all_paper_ids = submission_df["#"].tolist()
    number_co_bidders = {p1: {p2: 0 for p2 in all_paper_ids} for p1 in all_paper_ids}
    number_bidders = {p: 0 for p in all_paper_ids}
    for bid_level, weight in bid_level_weight.items():
        for bids in committee_df["bids_" + bid_level]:
            for i in range(len(bids) - 1):
                p1 = bids[i]
                if p1 in number_co_bidders:
                    number_bidders[p1] += weight
                    for j in range(i + 1, len(bids)):
                        p2 = bids[j]
                        if p2 in number_co_bidders:
                            number_co_bidders[p1][p2] += weight
                            number_co_bidders[p2][p1] += weight
    for p1, num_co_bidders in number_co_bidders.items():
        for p2 in number_co_bidders:
            denominator = number_bidders[p1] + number_bidders[p2]
            if denominator > 0:
                num_co_bidders[p2] /= denominator
    return number_co_bidders


def topic_similarity(submission_df: DataFrame):
    """Returns a dictionary mapping submission identifiers to a topic similarity dict. The latter is
    a dictionary mapping submissions to their topic similarity score.

    The topic similarity score between s1 and s2 is the number of topics assigned to both s1 and s2,
    divided by the number of topics assigned to either s1 or s2 (the Jaccard distance between sets
    of topics).

    Parameters
    ----------
        submission_df : pandas.DataFrame
            The submission dataframe
    """
    if "topics" not in submission_df.columns:
        raise ValueError(
            "There is no 'topics' column in the submission dataframe. Did you forget "
            "to pass a 'submission_topic_file_path' argument to the read_submission "
            "function?"
        )

    def pairwise_similarity(df_row, p1_id, p1_topics):
        p2_id = df_row["#"]
        p2_topics = df_row["topics"]
        size_intersection = 0
        size_union = len(p2_topics)
        for t in p1_topics:
            if t in p2_topics:
                size_intersection += 1
            else:
                size_union += 1
        if size_union > 0:
            similarity[p1_id][p2_id] = size_intersection / size_union
        else:
            similarity[p1_id][p2_id] = 0

    def compute_similarity(df_row):
        paper_id = df_row["#"]
        paper_topics = df_row["topics"]
        submission_df.apply(
            lambda r: pairwise_similarity(r, paper_id, paper_topics), axis=1
        )

    all_paper_ids = submission_df["#"].tolist()
    similarity = {p1: {p2: 0 for p2 in all_paper_ids} for p1 in all_paper_ids}

    submission_df.apply(compute_similarity, axis=1)

    return similarity
