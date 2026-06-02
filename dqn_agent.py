import numpy as np
import random
from collections import deque
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam

STATE_SIZE = 15
ACTION_SIZE = 3

GAMMA = 0.95
LEARNING_RATE = 0.001
EPSILON = 1.0
EPSILON_MIN = 0.05
EPSILON_DECAY = 0.995
MEMORY_SIZE = 2000
BATCH_SIZE = 32


class DQNAgent:

    def __init__(self):
        self.memory = deque(maxlen=MEMORY_SIZE)
        self.epsilon = EPSILON
        self.model = self._build_model()

    def _build_model(self):
        model = Sequential()
        model.add(Dense(64, input_dim=STATE_SIZE, activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(ACTION_SIZE, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(learning_rate=LEARNING_RATE))
        return model

    def remember(self, state, action, reward, next_state):
        self.memory.append((state, action, reward, next_state))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(ACTION_SIZE)

        q_values = self.model.predict(state, verbose=0)
        return np.argmax(q_values[0])

    def replay(self):

        if len(self.memory) < BATCH_SIZE:
            return

        minibatch = random.sample(self.memory, BATCH_SIZE)

        for state, action, reward, next_state in minibatch:

            target = reward + GAMMA * np.amax(
                self.model.predict(next_state, verbose=0)[0]
            )

            target_f = self.model.predict(state, verbose=0)
            target_f[0][action] = target

            self.model.fit(state, target_f, epochs=1, verbose=0)

        if self.epsilon > EPSILON_MIN:
            self.epsilon *= EPSILON_DECAY


agent = DQNAgent()
previous_state = None


# -------------------------------
# Normalized State
# -------------------------------
def create_state(metrics, predictions, active_vms):

    state = []

    for vm in active_vms:
        vm_data = metrics[vm]

        state.extend([
            vm_data.get("cpu", 0) / 100,
            vm_data.get("memory", 0) / 100,
            vm_data.get("network", 0) / 1000,
            vm_data.get("tasks", 0) / 50,
            predictions.get(vm, 0) / 100
        ])

    return np.reshape(np.array(state), [1, STATE_SIZE])


# -------------------------------
# Reward Function (Balanced)
# -------------------------------
def calculate_reward(metrics, active_vms, selected_vm):

    cpu_values = [metrics[vm]["cpu"] for vm in active_vms]
    vm_cpu = metrics[selected_vm]["cpu"]

    avg_load = np.mean(cpu_values)
    variance = np.var(cpu_values)

    reward = 0

    # Penalize imbalance
    reward -= variance * 0.4

    # Penalize high CPU
    reward -= vm_cpu * 0.2

    # Encourage balanced load
    reward -= abs(vm_cpu - avg_load) * 0.3

    # SLA penalty
    if vm_cpu >= 65:
        reward -= 25

    return reward


def select_vm(predictions, metrics, active_vms):

    global previous_state

    state = create_state(metrics, predictions, active_vms)

    action = agent.act(state)
    selected_vm = active_vms[action]

    reward = calculate_reward(metrics, active_vms, selected_vm)

    if previous_state is not None:
        agent.remember(previous_state, action, reward, state)
        agent.replay()

    previous_state = state

    print(f"[DQN] {selected_vm} | Reward: {reward:.2f} | Epsilon: {agent.epsilon:.3f}")

    return selected_vm, reward