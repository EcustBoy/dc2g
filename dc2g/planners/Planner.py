import os
import matplotlib.pyplot as plt
import glob
import imageio

class Planner:
    def __init__(self, name, traversable_colors, goal_color, room_or_object_goal, env_to_coor, env_next_coords, env_to_grid, env_grid_resolution, env_render):
        self.name = name
        self.traversable_colors = traversable_colors
        self.goal_color = goal_color
        self.room_or_object_goal = room_or_object_goal

        self.env_render = env_render

        self.step_number = 0
        self.project_path = os.path.dirname(os.path.realpath(__file__))+'/../..'
        self.individual_figure_path = self.project_path+'/dc2g/results'

        self.test_case_index = 0
        self.base_fig_name = "{test_case}_"+self.name+"{step}.{extension}"
        self.base_fig_path = self.individual_figure_path+"/{fig_type}/"
        self.base_fig_full_path = self.base_fig_path + self.base_fig_name

    def fig_filename(self, fig_type, extension, step=None):
        if step is None:
            step = "_"+str(self.step_number).zfill(3)
        return self.base_fig_full_path.format(
            step=step,
            fig_type=fig_type,
            test_case=str(self.test_case_index).zfill(3),
            extension=extension,
            )

    def step(self, obs):
        raise NotImplementedError

    def visualize(self):
        raise NotImplementedError

    def setup_plots(self, make_individual_figures, plot_panels, save_panel_figures, save_individual_figures, make_video):
        self.make_individual_figures = make_individual_figures
        self.plot_panels = plot_panels
        self.save_panel_figures = save_panel_figures
        self.save_individual_figures = save_individual_figures
        self.make_video = make_video
        
        if make_individual_figures:
            fig = plt.figure('C2G', figsize=(12, 12))
            plt.axis('off')
            fig = plt.figure('Observation', figsize=(12, 12))
            plt.axis('off')
            fig = plt.figure('Environment', figsize=(12, 12))
            plt.axis('off')
        if plot_panels:
            fig = plt.figure('DC2G', figsize=(24, 10))
            ax = fig.add_subplot(131)
            ax.set_axis_off()
            ax.set_title('2D Partial Semantic Map')
            ax = fig.add_subplot(132)
            ax.set_axis_off()
            ax.set_title('Predicted Cost-to-Go')
            ax = fig.add_subplot(133)
            ax.set_axis_off()
            ax.set_title('Planned Path')
            ax.set_xlabel("Red: Path\nBlue: Frontiers\nGray: Reachable Pts\nGreen: Reachable Cells to Push Frontier")
            plt.xticks(visible=False)
            plt.yticks(visible=False)

            # ax = fig.add_subplot(231)
            # ax.set_axis_off()
            # ax.set_title('World Semantic Map')
            # ax = fig.add_subplot(232)
            # ax.set_axis_off()
            # ax.set_title('True Cost-to-Go')
            # ax = fig.add_subplot(233)
            # ax.set_axis_off()
            # ax.set_title('Agent in Semantic Map')
            # total_world_array = plt.imread(world_image_filename)
            # world_id = world_image_filename.split('/')[-1].split('.')[0] # e.g. world00asdasdf
            # world_filetype = world_image_filename.split('/')[-1].split('.')[-1] # e.g. png
            # c2g_image_filename = '/home/mfe/code/dc2g/training_data/{dataset}/full_c2g/test/{world}{target}.{filetype}'.format(filetype=world_filetype, target=target, dataset=dataset, world=world_id)
            # total_c2g_array = plt.imread(c2g_image_filename)
            # plt.figure("DC2G")
            # plt.subplot(231)
            # plt.imshow(total_world_array)
            # plt.figure("DC2G")
            # plt.subplot(232)
            # plt.imshow(total_c2g_array)

    def plot(self, full_semantic_array):
        if self.plot_panels:
            plt.figure("DC2G")
            plt.suptitle('Step:' + str(self.step_number), fontsize=20)

            # render_mode = "rgb_array"
            # render = self.env_render(mode=render_mode, show_trajectory=True) # TODO: add support for show_trajectory to House3D
            # plt.subplot(233)
            # plt.imshow(render)
            # if make_individual_figures:
            #     plt.figure("Environment")
            #     plt.imshow(render)

            plt.figure("DC2G")
            plt.subplot(131)
            plt.imshow(full_semantic_array)
            # plt.imshow(render)

            if self.save_panel_figures or self.make_video:
                plt.figure("DC2G")
                plt.savefig(self.fig_filename("panels", "png"))
            if self.save_individual_figures:
                # plt.imsave("{individual_figure_path}/results/environment/step_{step_num}.png".format(individual_figure_path=self.individual_figure_path, step_num=str(self.step_number).zfill(3)), render)
                plt.imsave(self.fig_filename("observation", "png"), full_semantic_array)
            plt.pause(0.01)

    def animate_episode(self):
        if not self.make_video:
            return
        base_fig_name = self.base_fig_name
        plot_policy_name = self.name

        test_case_index = 0
        # Load all images of the current episode (each animation)
        fig_name = self.fig_filename("panels", "png", step="_*")
        last_fig_name = self.fig_filename("panels", "png")
        all_filenames = fig_name
        last_filename = last_fig_name
        
        # Dump all those images into a gif (sorted by timestep)
        print(all_filenames)
        filenames = glob.glob(all_filenames)
        filenames.sort()
        images = []
        for filename in filenames:
            print(filename)
            images.append(imageio.imread(filename))
        for i in range(10):
            images.append(imageio.imread(last_filename))
        for filename in filenames:
            os.remove(filename)

        # Save the gif in a new animations sub-folder
        animation_filename = self.fig_filename("animations", "gif", step="")
        os.makedirs(os.path.dirname(animation_filename), exist_ok=True)
        imageio.mimsave(animation_filename, images, duration=0.5)

        # convert .gif to .mp4
        cmd = "ffmpeg -y -i "+animation_filename+" -movflags faststart -pix_fmt yuv420p -vf 'scale=trunc(iw/2)*2:trunc(ih/2)*2' "+animation_filename[:-4]+".mp4"
        os.system(cmd)
