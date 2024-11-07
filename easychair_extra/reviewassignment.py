from __future__ import annotations

from mip import xsum, maximize, OptimizationStatus, Model, BINARY, LinExpr
from pandas import DataFrame


def committee_to_bid_profile(
    committee_df: DataFrame, submission_df: DataFrame, bid_levels: dict
):
    """Returns a dictionary mapping committee members to their bid profile. The latter is
    a dictionary mapping bid levels ("Yes", "No", "Maybe"...) to list of submission identifiers.

    Parameters
    ----------
        submission_df : pandas.DataFrame
            The submission dataframe
        committee_df : pandas.DataFrame
            The committee dataframe
        bid_levels : dict
            A dict indicating for each bid level a weight.
    """
    bid_profile = {}

    def apply_func(df_row):
        bids = {}
        for bid in bid_levels:
            bids[bid] = [
                p for p in df_row["bids_" + bid] if p in submission_df["#"].values
            ]
        bid_profile[df_row["#"]] = bids

    committee_df.apply(apply_func, axis=1)

    return bid_profile


def construct_mip_variables_for_assignment(bid_profile: dict, bid_weights: dict):
    """Based on a bid profiles and on weights for each bid level, constructs the variables
    for an ILP to compute a review assignment.

    This adds the following variables:
    - For each reviewer r, the binary variable y_r indicates whether r is used or not.
    - For each reviewer r and submission s, the binary variable x_r_s indicates whether r has been
     assigned s or not. These only exists for bids with strictly positive weight submitted by r.
    - For each submission s, the binary variable z_s indicated whether s is covered or not.

    Parameters
    ----------
        bid_profile : dict
            A bid profile as returned by the committee_to_bid_profile function.
        bid_weights : dict
            A dict indicating for each bid level a weight.
    """
    m = Model()
    reviewers_vars = {}
    reviewers_used_vars = {}
    submissions_vars = {}
    submissions_covered_vars = {}

    for r, bids in bid_profile.items():
        reviewers_vars[r] = {}
        reviewers_used_vars[r] = m.add_var(name=f"y_{r}", var_type=BINARY)
        for bid_level, bid_weight in bid_weights.items():
            if bid_weight > 0:
                for s in bids.get(bid_level, []):
                    variable = m.add_var(name=f"x_{r}_{s}", var_type=BINARY)
                    reviewers_vars[r][s] = variable
                    if s in submissions_vars:
                        submissions_vars[s][r] = variable
                    else:
                        submissions_vars[s] = {r: variable}
    for s in submissions_vars:
        submissions_covered_vars[s] = m.add_var(name=f"z_{s}", var_type=BINARY)
    return (
        m,
        reviewers_vars,
        reviewers_used_vars,
        submissions_vars,
        submissions_covered_vars,
    )


def find_feasible_review_assignment(
    bid_profile: dict,
    bid_weights: dict,
    max_num_reviews_asked: int,
    num_reviews_per_paper: int,
    min_num_reviewers: bool = False,
    verbose: bool = False,
) -> dict:
    """Runs an ILP to find a feasible reviewer assignment, that is, an assignment in which all
    submission are covered and no reviewer is assigned a paper they did not submit a bid with
    positive weight for.

    Parameters
    ----------
        bid_profile : dict
            A bid profile as returned by the committee_to_bid_profile function.
        bid_weights : dict
            A dict indicating for each bid level a weight.
        max_num_reviews_asked : int
            The maximum number of reviews assigned to a reviewer
        num_reviews_per_paper: int
            The number of reviewer that should be assigned to each submission.
        min_num_reviewers : bool, default to False
            If True, the number of reviewers used is minimised. Slow.
        verbose : bool, default to False
            If True, extra output is printed.
    """

    (
        m,
        reviewers_vars,
        reviewers_used_vars,
        submissions_vars,
        submissions_covered_vars,
    ) = construct_mip_variables_for_assignment(bid_profile, bid_weights)

    if max_num_reviews_asked is not None:
        for r, sub_vars in reviewers_vars.items():
            m += xsum(sub_vars.values()) <= max_num_reviews_asked
    for s, rev_vars in submissions_vars.items():
        m += xsum(rev_vars.values()) <= num_reviews_per_paper

    if min_num_reviewers:
        for r, sub_vars in reviewers_vars.items():
            for sub_var in sub_vars.values():
                m += reviewers_used_vars[r] >= sub_var

    objective = LinExpr()
    for r, bids in bid_profile.items():
        for bid_level, bid_weight in bid_weights.items():
            if bid_weight > 0:
                for s in bids.get(bid_level, []):
                    objective += reviewers_vars[r][s] * bid_weight

    if min_num_reviewers:
        objective *= (1 + num_reviews_per_paper) * len(bid_profile)  # big M
        objective -= xsum(reviewers_used_vars.values())
    m.objective = maximize(objective)

    m.verbose = verbose
    status = m.optimize(max_seconds=600)
    if verbose:
        if status == OptimizationStatus.OPTIMAL:
            print("optimal solution cost {} found".format(m.objective_value))
        elif status == OptimizationStatus.FEASIBLE:
            print(
                "sol.cost {} found, best possible: {}".format(
                    m.objective_value, m.objective_bound
                )
            )
        elif status == OptimizationStatus.NO_SOLUTION_FOUND:
            print(
                "no feasible solution found, lower bound is: {}".format(
                    m.objective_bound
                )
            )
    solution = None
    if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
        solution = {}
        for r, sub_vars in reviewers_vars.items():
            solution[r] = []
            for s, var in sub_vars.items():
                if abs(var.x) > 1e-6:
                    solution[r].append(s)
    return solution


def find_emergency_reviewers(
    bid_profile: dict, bid_weights: dict, max_num_reviewers: int, verbose: bool = False
) -> dict:
    """Runs an ILP to find a set of emergency reviewers. These are reviewers that can be asked last
    minute for extra review. The ILP searches for a set of reviewers of size no more than
    max_num_reviewers that maximises the number of covered submissions.

    Parameters
    ----------
        bid_profile : dict
            A bid profile as returned by the committee_to_bid_profile function.
        bid_weights : dict
            A dict indicating for each bid level a weight.
        max_num_reviewers : int
            The maximum size of the set of emergency reviewers
        verbose : bool, default to False
            If True, extra output is printed.
    """

    (
        m,
        reviewers_vars,
        reviewers_used_vars,
        submissions_vars,
        submissions_covered_vars,
    ) = construct_mip_variables_for_assignment(bid_profile, bid_weights)

    # Set up the constraints for the reviewers_used_vars
    for r, sub_vars in reviewers_vars.items():
        for sub_var in sub_vars.values():
            m += reviewers_used_vars[r] >= sub_var

    # Set up the constraints for the submissions_covered_vars
    for s, rev_vars in submissions_vars.items():
        m += submissions_covered_vars[s] <= xsum(rev_vars.values())

    # If the submission is covered and the reviewer is used, then we have to assign them the sub
    for r, sub_vars in reviewers_vars.items():
        for s, sub_var in sub_vars.items():
            m += sub_var >= submissions_covered_vars[s] + reviewers_used_vars[r] - 2

    m += xsum(reviewers_used_vars.values()) <= max_num_reviewers

    objective = xsum(submissions_covered_vars.values()) * len(submissions_vars) + xsum(xsum(v) for v in reviewers_vars.values())
    m.objective = maximize(objective)

    m.verbose = verbose
    status = m.optimize(max_seconds=600)
    if verbose:
        if status == OptimizationStatus.OPTIMAL:
            print("optimal solution cost {} found".format(m.objective_value))
        elif status == OptimizationStatus.FEASIBLE:
            print(
                "sol.cost {} found, best possible: {}".format(
                    m.objective_value, m.objective_bound
                )
            )
        elif status == OptimizationStatus.NO_SOLUTION_FOUND:
            print(
                "no feasible solution found, lower bound is: {}".format(
                    m.objective_bound
                )
            )

    solution = None
    if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
        solution = {}
        for r, v in reviewers_used_vars.items():
            if v.x > 1e-6:
                sol = []
                for bid_level, bids in bid_profile[r].items():
                    if bid_weights[bid_level] > 0:
                        sol.extend(bids)
                solution[r] = sol
    return solution
