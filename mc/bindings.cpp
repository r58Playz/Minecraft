#include <pybind11/pybind11.h>
#include "utils.hpp"

namespace py = pybind11;

PYBIND11_PLUGIN(utils)
{
    py::module m("utils");
    m.def("fade", &fade);
    m.def("lerp", &lerp);
    return m.ptr();
}
