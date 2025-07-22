from typing import ClassVar
from app import db
import sqlalchemy as sqla
import sqlalchemy.orm as sqlo
from pupil_apriltags import Detector


class AprilTag(db.Model):
    id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    
    tag_id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True, index=True)
    family : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(16))
    tag_size: sqlo.Mapped[float] = sqlo.mapped_column(default=0.1095)
    
    detector_id : sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey('april_tag_detector.id'))
    
    #relationships
    detector : sqlo.Mapped['AprilTagDetector'] = sqlo.relationship(back_populates='april_tags')


class AprilTagDetector(db.Model):
    id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    families : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(64), unique=True, index=True)

    nthreads : sqlo.Mapped[int] = sqlo.mapped_column(default=1)
    quad_decimate : sqlo.Mapped[float] = sqlo.mapped_column(default=1.0)
    quad_sigma : sqlo.Mapped[float] = sqlo.mapped_column(default=0.0)
    refine_edges : sqlo.Mapped[int] = sqlo.mapped_column(default=1)
    decode_sharpening : sqlo.Mapped[float] = sqlo.mapped_column(default=0.25)
    default_tag_size : sqlo.Mapped[float] = sqlo.mapped_column(default=0.1016)

    _detector: ClassVar[Detector] = None

    #relationships
    april_tags : sqlo.WriteOnlyMapped[AprilTag] = sqlo.relationship(back_populates='detector', passive_deletes=True)
    
    #functions
    def __repr__(self):
        return '<AprilTagDetector - {} "{}">'.format(self.id, self.families)

    def getDetector(self):
        if not self._detector:
            self._detector = Detector(
                families=self.families,
               nthreads=self.nthreads,
               quad_decimate=self.quad_decimate,
               quad_sigma=self.quad_sigma,
               refine_edges=self.refine_edges,
               decode_sharpening=self.decode_sharpening,
               debug=0
            )
        return self._detector

    def detect(self, image, camera_matrix):
        params = [camera_matrix[0, 0], camera_matrix[1, 1], camera_matrix[0, 2], camera_matrix[1, 2]]

        res = self.getDetector().detect(image, True, params, self.default_tag_size)

        tags = []

        for i in range(len(res)):
            tag = db.session.scalars(self.april_tags.select().where(AprilTag.tag_id == res[i].tag_id and AprilTag.family == res[i].tag_family)).first()
            if (tag):
                res[i].pose_t *= tag.tag_size / self.default_tag_size
                tags.append((i, tag))

        return (res, tags)