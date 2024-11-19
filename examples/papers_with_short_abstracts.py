# Help finding placeholder abstracts
# Ulle Endriss, 14 April 2024
import os

from easychair_extra.read import read_submission


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.join(current_dir, "..", "easychair_sample_files")

    # read submission and author files
    submissions = read_submission(
        os.path.join(root_dir, "submission.csv"),
        remove_deleted=True
    )
    submissions["abstract_len"] = submissions.apply(lambda df_row: len(df_row["abstract"]), axis=1)

    submissions.to_csv("abstract.csv", sep=",", encoding="utf-8", columns=["#", "abstract_len", "abstract"], index=False)


if __name__ == "__main__":
    main()

