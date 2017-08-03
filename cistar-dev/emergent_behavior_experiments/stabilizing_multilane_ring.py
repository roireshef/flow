"""
(document here)
"""

import logging

from rllab.envs.normalized_env import normalize
from rllab.misc.instrument import stub, run_experiment_lite
from rllab.baselines.linear_feature_baseline import LinearFeatureBaseline

from sandbox.rocky.tf.algos.trpo import TRPO
from sandbox.rocky.tf.policies.gaussian_mlp_policy import GaussianMLPPolicy
from sandbox.rocky.tf.envs.base import TfEnv

from cistar.envs.lane_changing import SimpleLaneChangingAccelerationEnvironment
from cistar.scenarios.loop.loop_scenario import LoopScenario
from cistar.controllers.rlcontroller import RLController
from cistar.controllers.lane_change_controllers import *
from cistar.controllers.car_following_models import *

logging.basicConfig(level=logging.INFO)

# stub(globals())

sumo_params = {"time_step": 0.1, "starting_position_shuffle": False, "vehicle_arrangement_shuffle": False,
               "rl_lc": "no_lat_collide", "human_lc": "strategic", "rl_sm": "no_collide", "human_sm": "no_collide"}
sumo_binary = "sumo"

env_params = {"target_velocity": 3, "max-deacc": -6, "max-acc": 3, "lane_change_duration": 0,
              "observation_vel_std": 0, "observation_pos_std": 0, "human_acc_std": 0.5, "rl_acc_std": 0}

net_params = {"length": 230, "lanes": 2, "speed_limit": 30, "resolution": 40,
              "net_path": "debug/net/", "lanes_distribution": 2}

cfg_params = {"start_time": 0, "end_time": 30000, "cfg_path": "debug/rl/cfg/"}

initial_config = {"shuffle": False, "bunching": 180}

num_cars = 15
num_auto = 1

exp_tag = str(num_cars) + '-car-' + str(num_auto) + \
          '-rl-stabilizing-multilane' \
          + "-%.2f-std" % (env_params["human_acc_std"])

type_params = {"rl": (num_auto, (RLController, {}), None, 0),
               "idm": (num_cars - num_auto, (IDMController, {}), (StaticLaneChanger, {}), 0)}

scenario = LoopScenario(exp_tag, type_params, net_params, cfg_params, initial_config=initial_config)

env = SimpleLaneChangingAccelerationEnvironment(env_params, sumo_binary, sumo_params, scenario)

env = TfEnv(normalize(env))

def run_task(v):
    policy = GaussianMLPPolicy(
        name="policy",
        env_spec=env.spec,
        hidden_sizes=(100, 50, 25)
    )

    baseline = LinearFeatureBaseline(env_spec=env.spec)

    algo = TRPO(
        env=env,
        policy=policy,
        baseline=baseline,
        batch_size=15000,
        max_path_length=1500,
        n_itr=500,
        # whole_paths=True,
        discount=0.999,
        step_size=0.01,
        n_vectorized_envs=1,
    )
    algo.train()

for seed in [5]:  # [22, 30, 67, 86]:
    run_experiment_lite(
        run_task,
        # Number of parallel workers for sampling
        n_parallel=1,
        # Only keep the snapshot parameters for the last iteration
        snapshot_mode="all",
        # Specifies the seed for the experiment. If this is not provided, a random seed
        # will be used
        seed=seed,
        mode="local",
        exp_prefix=exp_tag,
        # python_command="/home/aboudy/anaconda2/envs/rllab3/bin/python3.5"
        # plot=True,
    )
