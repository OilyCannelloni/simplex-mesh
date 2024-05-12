from mpl_toolkits.mplot3d.proj3d import proj_transform
from matplotlib.text import Annotation


class Annotation3D(Annotation):
    """Annotate the point xyz with text s"""

    def __init__(self, s, xyz, *args, **kwargs):
        Annotation.__init__(self, s, xy=(0, 0), *args, **kwargs)
        self._verts3d = xyz

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.xy = (xs, ys)
        Annotation.draw(self, renderer)

    @staticmethod
    def annotate3d(ax, s, *args, **kwargs):
        tag = Annotation3D(s, *args, **kwargs)
        ax.add_artist(tag)

