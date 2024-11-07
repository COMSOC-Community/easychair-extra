from __future__ import annotations

from pandas import DataFrame


def papers_without_pc(committee_df: DataFrame, submission_df: DataFrame):
    """Inserts a column in the submission dataframe called "no_author_pc" indicating
    whether at least one author of a submission is part of the program committee. This
    is "None" if all authors are students.

    Useful in case of policies such as: for every submission, one author can be asked to serve in
    the program committee.

    Parameters
    ----------
        submission_df : pandas.DataFrame
            The submission dataframe
        committee_df : pandas.DataFrame
            The committee dataframe
    """
    if "authors_id" not in submission_df.columns:
        raise ValueError("There is no 'authors_id' column in the submission dataframe. Did you "
                         "forget to pass a 'author_file_path' argument to the read_submission "
                         "function?")

    def aux(row):
        if row.get("all_authors_students"):
            return None
        return not any(a in committee_df["person #"].values for a in row["authors_id"])

    submission_df["no_author_pc"] = submission_df.apply(aux, axis=1)
