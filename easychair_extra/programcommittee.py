def papers_without_pc(committee_df, submission_df):
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
    def aux(row):
        if row["all_authors_students"]:
            return None
        return not any(a in committee_df["person #"].values for a in row["authors_id"])

    submission_df["no_author_pc"] = submission_df.apply(aux, axis=1)
