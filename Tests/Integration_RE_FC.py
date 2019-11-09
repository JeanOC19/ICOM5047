import Fiber_Density_Calculation
import Region_Extraction

dictionary = Region_Extraction.region_extraction_module(12, 3)

fiber_density = Fiber_Density_Calculation.fiber_density_calculation(3, 12, dictionary)

print(fiber_density)