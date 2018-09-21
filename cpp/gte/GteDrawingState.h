// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.0 (2014/08/11)

#pragma once

#include <gte/GteGraphicsObject.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

class GTE_IMPEXP DrawingState : public GraphicsObject
{
protected:
    // Abstract base class for grouping state classes.  This supports
    // simplification and reduction of member functions in the graphics engine
    // code.
    DrawingState();
};

}
