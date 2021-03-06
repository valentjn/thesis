// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.3 (2014/12/13)

#pragma once

#include <gte/GteFIQuery.h>
#include <gte/GteHalfspace.h>
#include <gte/GteHypersphere.h>
#include <gte/GteTIQuery.h>

// Queries for intersection of objects with halfspaces.  These are useful for
// containment testing, object culling, and clipping.

namespace gte
{

template <typename Real>
class TIQuery<Real, Halfspace3<Real>, Sphere3<Real>>
{
public:
    struct Result
    {
        bool intersect;
    };

    Result operator()(Halfspace3<Real> const& halfspace,
        Sphere3<Real> const& sphere);
};

//----------------------------------------------------------------------------
template <typename Real>
typename TIQuery<Real, Halfspace3<Real>, Sphere3<Real>>::Result
TIQuery<Real, Halfspace3<Real>, Sphere3<Real>>::operator()(
Halfspace3<Real> const& halfspace, Sphere3<Real> const& sphere)
{
    Result result;

    // Project the sphere center onto the normal line.  The plane of the
    // halfspace occurs at the origin (zero) of the normal line.
    Real center = Dot(halfspace.normal, sphere.center) - halfspace.constant;

    // The sphere and halfspace intersect when the projection interval
    // maximum is nonnegative.
    result.intersect = (center + sphere.radius >= (Real)0);
    return result;
}
//----------------------------------------------------------------------------

}
