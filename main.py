import meshcat
import meshcat.geometry as g
import time
import pinocchio as pin
import matplotlib.pyplot as plt
import numpy as np
import pickle
# from scipy.spatial.transform import Rotation as R

def interpolate_color(t, start_color, end_color):
    return list((1 - t) * start_color + t * end_color)

def compute_angular_velocity(rot_list, delta_t):
    """
    Computes the angular velocities from a list of 3x3 rotation matrices.

    Parameters:
    rot_list : list of np.ndarray
        List of 3x3 rotation matrices in SO(3).
    delta_t : float
        Time step between each rotation matrix.

    Returns:
    angular_velocities : list of float
        List of angular velocities
    """
    angular_velocities = []

    for i in range(1, len(rot_list)):
        R1 = rot_list[i - 1]
        R2 = rot_list[i]

        # Compute the relative rotation R12 = R1.T * R2
        R12 = R1.T @ R2

        # Compute the angular velocity vector (rotation vector)
        omega_body = np.linalg.norm(pin.log3(R12) / delta_t)
        angular_velocities.append(omega_body)
    return angular_velocities



def vis_rotations():
    function_dict = {
        'linear_angle_axis': interp_aa,
        'linear_quaternion': nlerp,
        'great_arc_quaternion': slerp,
    }
    # Set up the vis parameters
    num_frames = 20
    x_start = 0
    x_end = 4
    rotations_dict = pickle.load(open("rotations_dict.pkl", 'rb'))

    for rot_id in range(3):  # Only three test cases
        vis = meshcat.Visualizer().open()
        box_geometry = g.Box([0.3, 0.6, 0.1])  # shape to move
        angular_velocities_list = []

        for i, (func_name, func) in enumerate(function_dict.items()):
            rot_list = []
            r0, ri, r1 = rotations_dict[func_name][rot_id]
            for j in range(num_frames):
                t = j / (num_frames - 1)  # Normalized time for interpolation
                x_position = (1 - t) * x_start + t * x_end
                interp_rot = func(r0, ri, r1, t)
                rot_list.append(interp_rot.copy())

                # transform of cuboid that shows the rotation evolution
                transform = np.eye(4)
                transform[:3, :3] = interp_rot.copy()
                transform[0, 3] = x_position
                transform[1, 3] = i

                vis[f"rectangle_{i}_{j}"].set_object(box_geometry)
                # Set color gradient
                color = interpolate_color(t, np.array([0, 0, 1, 0.7]), np.array([1, 0, 0, 0.7]))
                vis[f"rectangle_{i}_{j}"].set_property('color', color)
                vis[f"rectangle_{i}_{j}"].set_transform(transform)
            angular_velocities_list.append(compute_angular_velocity(rot_list, 1/num_frames))

        fig, ax = plt.subplots(1, 1, figsize=(10, 8), sharex=True)
        fig.suptitle('Angular Velocities Comparison')
        # Colors and labels for the four lists
        labels = list(function_dict.keys())
        colors = plt.cm.tab10.colors[:len(labels)]
        num_timesteps = len(angular_velocities_list[0])
        time_array = np.arange(num_timesteps) * 1/num_frames
        # Plot angular velocity
        for j, component_values in enumerate(angular_velocities_list):
            ax.plot(time_array, component_values, label=labels[j], color=colors[j], alpha=0.7)
            ax.annotate(
                '',
                xy=(time_array[2 * j], component_values[2 * j]),
                xytext=(time_array[2 * j] - 0.5, component_values[2 * j] + 0.5 * np.sign(component_values[2 * j])),
                arrowprops=dict(facecolor=colors[j], shrink=0.05, width=1, headwidth=8)
            )

            ax.set_ylabel(f'Ang vel (rad/s)')
            ax.legend(loc="upper right")
            ax.grid(True)

        # Set the x-axis label on the bottom plot
        ax.set_xlabel('Time (s)')
        plt.tight_layout()
        plt.subplots_adjust(top=0.92)  # Adjust for the main title
        plt.show()

        time.sleep(1)
    time.sleep(5.)

if __name__ == '__main__':
    vis_rotations()
