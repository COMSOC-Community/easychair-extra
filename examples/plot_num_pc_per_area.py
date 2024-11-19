from collections import Counter, defaultdict

import os.path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from easychair_extra.read import read_committee, read_topics

AREA_NICKNAMES = {
    "Fairness, Ethics, and Trust": "FAIR",
    "Computer Vision": "CV",
    "Constraints and Satisfiability": "CONSAT",
    "Data Mining": "DATA",
    "Knowledge Representation and Reasoning": "KRR",
    "Humans and AI": "HUM",
    "Machine Learning": "ML",
    "Multiagent Systems": "MAS",
    "Natural Language Processing": "NLP",
    "Planning and Search": "PLAN",
    "Robotics": "ROBO",
    "Uncertainty in AI": "UAI",
    "Multidisciplinary Topics": "MULT",
}

AREA_NICKNAMES_SWAPPED = {
    "FAIR": "Fairness, Ethics, and Trust",
    "CV": "Computer Vision",
    "CONSAT": "Constraints and Satisfiability",
    "DATA": "Data Mining",
    "KRR": "Knowledge Representation and Reasoning",
    "HUM": "Humans and AI",
    "ML": "Machine Learning",
    "MAS": "Multiagent Systems",
    "NLP": "Natural Language Processing",
    "PLAN": "Planning and Search",
    "ROBO": "Robotics",
    "UAI": "Uncertainty in AI",
    "MULT": "Multidisciplinary Topics",
}

ROLE_NICKNAMES = {
    "associate chair": "AC",
    "senior PC member": "SPC",
    "chair": "PCC",
    "PC member": "PC",
}


def compute_area_topic_to_weight(committee_df, topics_to_areas):
    # We initialise some dicts that hold the information.
    topics_to_pcs = defaultdict(lambda: defaultdict(list))  # topics => dict[role, list of PCs]
    num_topics_per_pc = Counter()

    def populate_pc_dicts(df_row):
        pc_id = df_row["#"]
        r = df_row["role"]
        num_topics_per_pc[pc_id] += 1
        for t in df_row["topics"]:
            topics_to_pcs[t][r].append(pc_id)

    # Populate the dicts initialised above
    committee_df.apply(populate_pc_dicts, axis=1)

    # We replace the PC members ids by their weight, for the topic dict
    topics_to_weight = {}
    for topic, role_dict in topics_to_pcs.items():
        topics_to_weight[topic] = dict()
        for role, pc_list in role_dict.items():
            if role not in topics_to_weight[topic]:
                topics_to_weight[topic][role] = sum(
                    1 / num_topics_per_pc[pc] for pc in pc_list
                )

    # We sum up for the areas:
    areas_to_weight = {}
    for topic, role_dict in topics_to_weight.items():
        area = topics_to_areas[topic]  # The area corresponding to the topic
        if area not in areas_to_weight:
            areas_to_weight[area] = dict()
        for role, weight in role_dict.items():
            if role not in areas_to_weight[area]:
                areas_to_weight[area][role] = weight
            else:
                areas_to_weight[area][role] += weight

    return areas_to_weight, topics_to_weight


def plot_requirement_vs_practice(
    area_weights,
):
    all_areas = sorted(AREA_NICKNAMES)
    all_roles = ["associate chair", "senior PC member", "PC member"]

    # Prepare the pandas frame
    data = []
    for area in all_areas:
        for role in all_roles:
            actual_value = area_weights[area].get(role, 0)
            data.append(
                {"area": area, "role": role, "type": "current", "value": actual_value}
            )

    df = pd.DataFrame(data)

    plt.close("all")
    g = sns.catplot(
        data=df,
        x="role",
        y="value",
        col="area",
        col_wrap=3,
        kind="bar",
        sharey=False,
        sharex=False,
    )

    # Add the values on top
    for ax in g.axes.ravel():
        for c in ax.containers:
            labels = []
            for v in c:
                height = v.get_height()
                if int(height) == height or height > 10:
                    labels.append(str(round(height)))
                else:
                    labels.append(f"{height:.1f}")
            ax.bar_label(c, labels=labels, label_type="edge")
        ax.margins(y=0.2)

    g.set_titles("{col_name}")
    g.set_axis_labels("", "Count")

    plt.show()


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.join(current_dir, "..", "easychair_sample_files")

    # Read the committee file with the bids
    committee_df = read_committee(
        os.path.join(root_dir, "committee.csv"),
        committee_topic_file_path=os.path.join(root_dir, "committee_topic.csv")
    )

    area_topic_mapping, topic_area_mapping = read_topics(os.path.join(root_dir, "topics.csv"))

    # Compute the weight per area and per role
    area_weight_map, topic_weight_map = compute_area_topic_to_weight(committee_df, topic_area_mapping)
    plot_requirement_vs_practice(
        area_weight_map,
    )


if __name__ == "__main__":
    main()
