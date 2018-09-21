// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.2 (2014/12/13)

#pragma once

#include <gte/GteDistPoint3Frustum3.h>
#include <gte/GteFrustum3.h>
#include <gte/GteHypersphere.h>
#include <gte/GteTIQuery.h>

namespace gte
{

template <typename Real>
class TIQuery<Real, Sphere3<Real>, Frustum3<Real>>
{
public:
    struct Result
    {
        bool intersect;
    };

    Result operator()(Sphere3<Real> const& sphere,
        Frustum3<Real> const& frustum);
};

//----------------------------------------------------------------------------
template <typename Real>
typename TIQuery<Real, Sphere3<Real>, Frustum3<Real>>::Result
TIQuery<Real, Sphere3<Real>, Frustum3<Real>>::operator()(
Sphere3<Real> const& sphere, Frustum3<Real> const& frustum)
{
    Result result;
    DCPQuery<Real, Vector3<Real>, Frustum3<Real>> vfQuery;
    Real distance = vfQuery(sphere.center, frustum).distance;
    result.intersect = (distance <= sphere.radius);
    return result;
}
//----------------------------------------------------------------------------

}
