from unityagents import UnityEnvironment
import matplotlib.pyplot as plt
import numpy as np
from skimage import transform
from skimage.color import rgb2gray
from collections import deque
import torch

from model import QNetwork
from agent import Agent

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

env = UnityEnvironment(file_name="Banana.app")

brain_name = env.brain_names[0]
brain = env.brains[brain_name]

# reset the environment
env_info = env.reset(train_mode=False)[brain_name]

# number of agents in the environment
n_agents = len(env_info.agents)
# print('Number of agents: ', n_agents)

# number of actions
action_size = brain.vector_action_space_size
# print('Action Size: ', action_size)

# examine the state space
state = np.squeeze(env_info.visual_observations[0])
state_size = state.shape
print('States have shape: ', state_size)
# print('States look like:')
# plt.figure()
# plt.imshow(state)
# plt.show()
# state = np.reshape(state, [3, 84, 84])
# state_size = state.shape
# print('States have shape: ', state_size)

stack_size = 4

# Initialize deque with zero-images. One array for each image
stacked_frames = deque([np.zeros((3, 84, 84), dtype=np.int) for _ in range(stack_size)], maxlen=4)


def stack_frames(stacked_frames, state, is_new_episode):

    frame = np.squeeze(state)

    if is_new_episode:
        # Clear our stacked frames
        stacked_frames = deque([np.zeros((3, 84, 84), dtype=np.int) for _ in range(stack_size)], maxlen=4)

        # Because we're in a new episode,copy the same frame 4 times
        stacked_frames.append(frame)
        stacked_frames.append(frame)
        stacked_frames.append(frame)
        stacked_frames.append(frame)

        # Stack the frames
        stacked_state = np.stack(stacked_frames, axis=0)

    else:
        # Append frame to deque, automatically removes the oldest frame
        stacked_frames.append(frame)

        # Build the stacked state (first dimension specifies different frames)
        stacked_state = np.stack(stacked_frames, axis=0)

    return stacked_state, stacked_frames

# agent = Agent()
qnetwork = QNetwork(action_size).to(device)

for _ in range(5):
    env_info = env.reset(train_mode=True)[brain_name]
    state = np.reshape(np.squeeze(env_info.visual_observations[0]), [3, 84, 84])
    stacked_state, stacked_frames = stack_frames(stacked_frames, state, is_new_episode=True)
    for t in range(1000):
        # action = np.random.randint(4)
        with torch.no_grad():
            action_values = qnetwork(torch.from_numpy(stacked_state).float().to(device))
        action = np.argmax(action_values.cpu().data.numpy())
        print('action_chosen: ', action)
        print(action.dtype)
        env_info = env.step(np.int(action))[brain_name]
        next_state = np.reshape(np.squeeze(torch.from_numpy(env_info.visual_observations[0])), [3, 84, 84])
        stacked_next_state, stacked_frames = stack_frames(stacked_frames, next_state, is_new_episode=False)
        reward = env_info.rewards[0]
        done = env_info.local_done[0]
        # agent.step(state, action, reward, next_state, done)
        # for i in range(4):
        #     plt.imshow(stacked_state[:,:,:,i])
        #     plt.show()
        state = next_state
        stacked_state = stacked_next_state
        if done:
            break


# agent = Agent(state_size=state_size, action_size=action_size, seed=0)


# def dqn(n_episodes = 2000, max_t=1000, epsilon_start=1.0, epsilon_end=0.01, epsilon_decay=0.98):
#     """Deep Q-Learning
#
#     Params:
#         n_episodes (int): maximum number of training episodes
#         max_t (int): maximum number of time-steps per episode
#         epsilon_start (float): starting value of epsilon, for epsilon-greedy action selection
#         epsilon_end (float): minimum value of epsilon
#         epsilon_decay (float): multiplicative factor (per episode) for decreasing epsilon"""
#
#     scores = []
#     scores_window = deque(maxlen=100)
#     epsilon = epsilon_start
#
#     for i_episode in range(1, n_episodes+1):
#         env_info = env.reset(train_mode=True)[brain_name]           # Reset environment to start from the beginning
#         state = env_info.vector_observations[0]                     # Get the current state
#         score = 0                                                   # Set the score to 0 before the episode begins
#         for t in range(max_t):
#             action = int(agent.act(state, epsilon))                 # The agent selects an action
#             env_info = env.step(action)[brain_name]                 # Take chosen action in the environment
#             next_state = env_info.vector_observations[0]            # Get the next state from the environment
#             reward = env_info.rewards[0]                            # Get the reward for taking selected action
#             done = env_info.local_done[0]                           # Check to see if the episode has terminated or completed
#             agent.step(state, action, reward, next_state, done)     # The agent learns from a sampled set of experiences
#             state = next_state                                      # Set the state as the new_state or current state of the env
#             score +=reward                                          # Update the scores based on rewards
#             if done:
#                 break                                               # Break the loop after the episode has completed
#         scores_window.append(score)
#         scores.append(score)
#         epsilon = max(epsilon_end, epsilon*epsilon_decay)
#         print('\rEpisode {}\tAverage Score: {:.2f}'.format(i_episode, np.mean(scores_window), end=""))
#         if i_episode % 100 == 0:
#             print('\rEpisode {}\tAverage Score: {:.2f}'.format(i_episode, np.mean(scores_window)))
#         if np.mean(scores_window)>=13.0:
#             # Once the episode has been solved, store the weights in a file
#             # This allows us to use the trained agent to test with later on without having to retrain it every time
#             print('\nEnvironment solved in {:d} episodes!\tAverage Score: {:.2f}'.format(i_episode-100, np.mean(scores_window)))
#             torch.save(agent.qnetwork_local.state_dict(), 'checkpoint.pth')
#             break
#
#     return scores


# fig = plt.figure()                              # Plotting the graph showing the increase in Q-Value as
# plt.xlabel('Episodes')                          # we progress through more episodes and gain more experience
# plt.ylabel('Scores')
# plt.plot(np.arange(len(scores)), scores)
# plt.show()



env.close()