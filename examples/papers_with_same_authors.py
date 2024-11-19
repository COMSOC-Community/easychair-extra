import os

import pandas as pd

from easychair_extra.read import read_submission, read_committee


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Read the submission file
    submissions = read_submission(
        os.path.join(current_dir, "..", "easychair_sample_files", "submission.csv"),
        author_file_path=os.path.join(current_dir, "..", "easychair_sample_files", "author.csv"),
    )

    # Add a column with the number of authors
    submissions["num_authors"] = submissions.apply(
        lambda x: len(x["authors_id"]), axis=1
    )
    submissions.sort_values("num_authors", inplace=True, ascending=False)

    duplicated_authors = submissions[submissions.duplicated(subset=["authors_id"])][
        "authors_id"
    ].unique()

    print(f"These author_sets have one or more submission: {duplicated_authors}")
    for authors in duplicated_authors:
        print("=" * 20 + f"\nAuthor set: {authors}")
        with pd.option_context(
            "display.max_rows", None, "display.max_columns", None, "display.width", 500
        ):
            print(
                submissions[submissions["authors_id"] == authors][
                    ["#", "title", "authors_id", "authors"]
                ].to_string(index=False)
            )


if __name__ == "__main__":
    main()
