#####################################

ds, s, probs, ol, result = RX_pulse(RX, sigma, current_state, plot_prob=False, plot_blochsphere=False)
    print("|0>", probs[0], "---", "|1>", probs[1], "---", ds, s, "final:", result[-1].data)

ds, s, probs, ol, result = RZ_pulse(RZ, sigma, current_state, plot_prob=False, plot_blochsphere=False)
    print("|0>", probs[0], "---", "|1>", probs[1], "---", ds, s, "final:", result[-1].data)



#####################################
drive_strength_samples = np.linspace(0, 0.02277960635661175, samples)
sigma_samples = np.linspace(15, 15, samples)
def h_pulse(drive_strength, sigma, plot, bool_blochsphere=False):
    expected_state = np.array([1, 1]) / np.sqrt(2)
    phase = np.pi / 2

    omega = 5.0                         # v
    drive_strength = drive_strength     # r
    sigma = sigma                       # sigma

    final_probs = np.zeros(2)

    H_static = static_hamiltonian(omega=omega)
    H_drive = drive_hamiltonian(drive_strength=drive_strength)

    ham_solver = Solver(
        static_hamiltonian=H_static,
        hamiltonian_operators=[H_drive],
        rotating_frame=H_static
    )

    duration = 120  # Number of time steps (samples)
    amp = 1.0      # Amplitude, height gaussian bell at peak, default Max
    _dt = 0.1       # Time step in ns
    t_span = np.linspace(0, duration * _dt, duration + 1)   # Tells solver when to check the qubits state

    def gaussian_envelope(t):
        center = duration * _dt / 2
        return amp * jnp.exp(-((t - center) ** 2) / (2 * sigma ** 2))

    gaussian_signal = Signal(
        envelope=gaussian_envelope,
        carrier_freq=omega,
        phase=phase
    )
    result = ham_solver.solve(
        t_span=t_span,
        y0=INIT_STATE,
        method='jax_odeint',
        signals=[gaussian_signal]
    )
    state_probs = prob(result.y)
    final_state = result.y[-1]
    overlap = np.abs(np.vdot(expected_state, final_state)) ** 2

    final_probs[0] = state_probs[-1, 0]
    final_probs[1] = state_probs[-1, 1]

    if plot:
        plot_probabilities(t_span, state_probs)
    if bool_blochsphere:
        plot_bloch_sphere(result.y)

    return drive_strength, sigma, final_probs, overlap, result.y


def RX_pulse(drive_strength, sigma, theta, plot=False, bool_blochsphere=False):
    final_probs = np.zeros(2)
    omega = 5.0
    H_static = static_hamiltonian(omega=omega)
    H_drive = drive_hamiltonian(drive_strength=drive_strength)
    ham_solver = Solver(
        static_hamiltonian=H_static,
        hamiltonian_operators=[H_drive],
        rotating_frame=H_static
    )
    duration = 120
    amp = 1.0
    _dt = 0.1
    t_span = np.linspace(0, duration * _dt, duration + 1)

    def gaussian_envelope(t):
        center = duration * _dt / 2
        return amp * jnp.exp(-((t - center) ** 2) / (2 * sigma ** 2))
    gaussian_signal = Signal(
        envelope=gaussian_envelope,
        carrier_freq=omega,
        phase=0  # Set to 0 for X-axis rotation
    )
    result = ham_solver.solve(
        t_span=t_span,
        y0=INIT_STATE,
        method='jax_odeint',
        signals=[gaussian_signal]
    )

    if plot:
        state_probs = np.abs(result.y) ** 2
        plt.figure(figsize=(10, 6))
        plt.plot(t_span, state_probs[:, 0], label="P(|0>)")
        plt.plot(t_span, state_probs[:, 1], label="P(|1>)")
        plt.xlabel("Time (ns)")
        plt.ylabel("Probability")
        plt.title("Qubit State Evolution Under Gaussian Pulse for RX gate")
        plt.legend()
        plt.grid()
        plt.show()
    if bool_blochsphere:
        plot_bloch_sphere(result.y)
    expected_state = np.array([np.cos(theta/2), -1j * np.sin(theta/2)])
    final_state = result.y[-1]
    overlap = np.abs(np.vdot(expected_state, final_state)) ** 2
    state_probs = np.abs(result.y) ** 2
    final_probs[0] = state_probs[-1, 0]
    final_probs[1] = state_probs[-1, 1]
    return drive_strength, sigma, final_probs, overlap, result.y


def RZ_pulse(drive_strength, sigma, theta, plot=False, bool_blochsphere=False):
    final_probs = np.zeros(2)
    omega = 5.0
    H_static = static_hamiltonian(omega=omega)
    H_drive = drive_hamiltonian(drive_strength=drive_strength)
    ham_solver = Solver(
        static_hamiltonian=H_static,
        hamiltonian_operators=[H_drive],
        rotating_frame=H_static
    )
    duration = int(theta / (omega * 0.1))  # Adjust duration for theta, assuming _dt=0.1
    if duration < 1:
        duration = 1
    amp = 1.0
    _dt = 0.1
    t_span = np.linspace(0, duration * _dt, duration + 1)

    def gaussian_envelope(t):
        center = duration * _dt / 2
        return amp * jnp.exp(-((t - center) ** 2) / (2 * sigma ** 2))
    gaussian_signal = Signal(
        envelope=gaussian_envelope,
        carrier_freq=omega,
        phase=0  # Set to 0 for Z-axis alignment
    )
    result = ham_solver.solve(
        t_span=t_span,
        y0=INIT_STATE,
        method='jax_odeint',
        signals=[gaussian_signal]
    )
    if plot:
        state_probs = np.abs(result.y) ** 2
        plt.figure(figsize=(10, 6))
        plt.plot(t_span, state_probs[:, 0], label="P(|0>)")
        plt.plot(t_span, state_probs[:, 1], label="P(|1>)")
        plt.xlabel("Time (ns)")
        plt.ylabel("Probability")
        plt.title("Qubit State Evolution Under Gaussian Pulse for RZ gate")
        plt.legend()
        plt.grid()
        plt.show()
    if bool_blochsphere:
        plot_bloch_sphere(result.y)
    expected_state = np.array([np.exp(-1j*theta/2), 0])  # For |0> initially
    final_state = result.y[-1]
    overlap = np.abs(np.vdot(expected_state, final_state)) ** 2
    state_probs = np.abs(result.y) ** 2
    final_probs[0] = state_probs[-1, 0]
    final_probs[1] = state_probs[-1, 1]
    return drive_strength, sigma, final_probs, overlap, result.y


def estimate_period_zero_crossing(x, f_x):
    zero_crossings = np.where(np.diff(np.sign(f_x)))[0]
    if len(zero_crossings) > 1:
        T_est = np.mean(np.diff(x[zero_crossings])) * 2  # Assuming half-period per crossing
        return T_est
    else:
        return None

def estimate_period(x, f_x):
    peaks, _ = find_peaks(f_x)  # Find local maxima
    if len(peaks) > 1:
        T_est = np.mean(np.diff(x[peaks]))  # Average distance between peaks
        return T_est
    else:
        return None