export function resolveEntryCopy(step) {
  const MAP = {
    create_experiment: "setting up your experiment",
    define_experiment: "defining your experiment",
    design_parameters: "designing the experiment",
    phase3_feasibility: "reviewing experiment feasibility",
    phase3_decision: "making a decision",
    phase4_implementation: "implementing the experiment",
    analysis_completed: "reviewing results",
    experiment_completed: "finalizing the experiment",
  };

  return MAP[step] || "working on this experiment";
}