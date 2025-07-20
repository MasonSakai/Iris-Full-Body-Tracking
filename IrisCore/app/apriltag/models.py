from app import db
import sqlalchemy as sqla
import sqlalchemy.orm as sqlo
from pupil_apriltags import Detector


class AprilTagDetector(db.Model):
	id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
	families : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(64), unique=True, index=True)

	nthreads : sqlo.Mapped[int] = sqlo.mapped_column(default=1)
	quad_decimate : sqlo.Mapped[float] = sqlo.mapped_column(default=1.0)
	quad_sigma : sqlo.Mapped[float] = sqlo.mapped_column(default=0.0)
	refine_edges : sqlo.Mapped[int] = sqlo.mapped_column(default=1)
	decode_sharpening : sqlo.Mapped[float] = sqlo.mapped_column(default=0.25)

	
	#functions
	def __repr__(self):
		return '<AprilTagDetector - {} "{}">'.format(self.id, self.families)

	def createDetector(self):
		return Detector(
		   families=self.families,
		   nthreads=self.nthreads,
		   quad_decimate=self.quad_decimate,
		   quad_sigma=self.quad_sigma,
		   refine_edges=self.refine_edges,
		   decode_sharpening=self.decode_sharpening,
		   debug=0
		)
