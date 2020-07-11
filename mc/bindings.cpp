#include <pybind11/pybind11.h>
#include "perlin.hpp"

namespace py = pybind11;

PYBIND11_PLUGIN(perlin_helper)
{
    py::module m("perlin_helper");
    m.def("fade", &fade);
    m.def("lerp", &lerp);
    return m.ptr();
}
