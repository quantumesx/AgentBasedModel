"""Animate a trial."""

from matplotlib import pyplot as plt
from matplotlib import animation


def animate(trial, name='unnamed_trial'):
    """
    Animate a trial.

    input: a trial object
    output: saved animation file in local directory
    """
    fig = plt.figure()
    fig.set_dpi(100)
    fig.set_size_inches(5, 5)

    ax = plt.axes(xlim=(0, 270), ylim=(0, 270))
    agents = trial.env.agents

    target1 = plt.Circle((80, 80), 35, fc='gray')
    target2 = plt.Circle((190, 190), 35, fc='gray')
    a0 = plt.Circle(agents[0].loc_data[0], 2.6, fc='red')
    a1 = plt.Circle(agents[1].loc_data[0], 2.6, fc='orange')
    a2 = plt.Circle(agents[2].loc_data[0], 2.6, fc='cyan')
    a3 = plt.Circle(agents[3].loc_data[0], 2.6, fc='green')

    def init():
        a0.center = agents[0].loc_data[0]
        a1.center = agents[1].loc_data[0]
        a2.center = agents[2].loc_data[0]
        a3.center = agents[3].loc_data[0]

        ax.add_patch(target1)
        ax.add_patch(target2)
        ax.add_patch(a0)
        ax.add_patch(a1)
        ax.add_patch(a2)
        ax.add_patch(a3)

        return []

    def animationManage(i, a0, a1, a2, a3):
        animate0(i, a0)
        animate1(i, a1)
        animate2(i, a2)
        animate3(i, a3)

        return []

    def animate0(i, patch):
        patch.center = agents[0].loc_data[i]
        return patch,

    def animate1(i, patch):
        patch.center = agents[1].loc_data[i]
        return patch,

    def animate2(i, patch):
        patch.center = agents[2].loc_data[i]
        return patch,

    def animate3(i, patch):
        patch.center = agents[3].loc_data[i]
        return patch,

    anim = animation.FuncAnimation(fig, animationManage,
                                   init_func=init,
                                   frames=1000,
                                   fargs=(a0, a1, a2, a3, ),
                                   interval=20,
                                   blit=True,
                                   repeat=True)

    plt.show()
    anim.save('Data/Animation/'+name+'.mp4', fps=100, extra_args=['-vcodec',
                                                                  'libx264'])
