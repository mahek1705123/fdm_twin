"""Value objects. DesignInput is validated once at the edge and trusted everywhere else."""
from dataclasses import dataclass, asdict

from .constants import ANGLES, MATERIALS, RANGES, TOPOLOGIES


class DomainError(ValueError):
    """Raised for invalid user input; the API layer turns it into HTTP 400."""


@dataclass(frozen=True)
class DesignInput:
    topology: str
    angle: float
    material: str
    cell_size: float
    wall_thickness: float
    layer_thickness: float
    nozzle_temp: float

    @classmethod
    def from_dict(cls, d: dict) -> "DesignInput":
        try:
            obj = cls(
                topology=str(d["topology"]), angle=float(d["angle"]), material=str(d["material"]),
                cell_size=float(d["cell_size"]), wall_thickness=float(d["wall_thickness"]),
                layer_thickness=float(d["layer_thickness"]), nozzle_temp=float(d["nozzle_temp"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise DomainError(f"Invalid or missing design field: {exc}") from exc
        obj.validate()
        return obj

    def validate(self) -> None:
        if self.topology not in TOPOLOGIES:
            raise DomainError(f"Unknown topology '{self.topology}'")
        if self.material not in MATERIALS:
            raise DomainError(f"Unknown material '{self.material}'")
        if self.angle not in ANGLES[self.topology]:
            raise DomainError(f"Angle {self.angle} is not available for {self.topology}: use {ANGLES[self.topology]}")
        for field, (lo, hi, _) in RANGES.items():
            if not lo <= getattr(self, field) <= hi:
                raise DomainError(f"{field} must be between {lo} and {hi}")

    def with_(self, **kw) -> "DesignInput":
        return DesignInput(**{**asdict(self), **kw})

    def as_row(self) -> dict:
        """Row in the column layout used by the trained pipelines."""
        return {
            "Cell_Size_L_mm": self.cell_size, "Wall_Thickness_T_mm": self.wall_thickness,
            "Reentrant_Angle_deg": self.angle, "Layer_Thickness_mm": self.layer_thickness,
            "Nozzle_Temp_C": self.nozzle_temp, "Topology_Type": self.topology, "Material": self.material,
        }
