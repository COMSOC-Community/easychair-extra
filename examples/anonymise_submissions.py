# Make file with anonymised submissions to share with sister conferences
# (for dual-submission detection)
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

    submissions["id"] = submissions["#"]
    submissions.to_csv("anonymised_submissions.csv", sep=",", encoding="utf-8", columns=["id", "title", "abstract"], index=False)


if __name__ == "__main__":
    main()
