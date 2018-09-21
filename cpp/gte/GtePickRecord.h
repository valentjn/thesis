// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.2 (2014/12/13)

#pragma once

#include <gte/GteIndexFormat.h>
#include <gte/GteVector4.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

class Visual;

class GTE_IMPEXP PickRecord
{
public:
    // Construction and destruction.  The default constructor does not
    // initialize any members.  It exists to support the construction
    // of the const static PickRecord in the Picker class.
    ~PickRecord();
    PickRecord();

    // For sorting purposes.
    inline bool operator==(PickRecord const& record) const;
    inline bool operator!=(PickRecord const& record) const;
    inline bool operator< (PickRecord const& record) const;
    inline bool operator<=(PickRecord const& record) const;
    inline bool operator> (PickRecord const& record) const;
    inline bool operator>=(PickRecord const& record) const;

    // The object for which some primitive satisfies the picking criteria.
    // The vertexIndex[] are relative to the vertex buffer array of the
    // 'visual'.  If the primitive is a triangle, then all three indices are
    // valid.  If the primitive is a segment, then the first two indices are
    // valid.  If the primitive is a point, then the first index is valid.
    // The invalid indices are set to -1.
    Visual* visual;
    IPType primitiveType;
    int primitiveIndex;
    int vertexIndex[3];

    // The linear component is parameterized by P + t*D.  The t-value
    // corresponds to the point of intersection when the primitive is a
    // triangle.  For point and segment primitives, the t-value corresponds
    // to the closest point to the primitive.  Sorting of PickRecord-s is
    // based on the t-value.
    float t;
    Vector4<float> linePoint;

    // The barycentric coordinates of the point of intersection when the
    // primitive is a triangle or of the closest primitive point when the
    // primitive is a segment or a point.  The coordinates have the
    // properties 0 <= bary[i] <= 1 and bary[0] + bary[1] + bary[2] = 1.
    // For a triangle, all three bary[] values are potentially positive.
    // For a segment, bary[2] = 0.  For a point, bary[0] = 1 and bary[1]
    // = bary[2] = 0.  The order of the bary[] values is consistent with
    // the ordering of the vertices of the primitive.
    float bary[3];
    Vector4<float> primitivePoint;

    // The distance between line point and primitive point.  This is zero
    // when the primitives are triangles.
    float distance;
};

//----------------------------------------------------------------------------
inline bool PickRecord::operator==(PickRecord const& record) const
{
    return t == record.t;
}
//----------------------------------------------------------------------------
inline bool PickRecord::operator!=(PickRecord const& record) const
{
    return t != record.t;
}
//----------------------------------------------------------------------------
inline bool PickRecord::operator< (PickRecord const& record) const
{
    return t < record.t;
}
//----------------------------------------------------------------------------
inline bool PickRecord::operator<=(PickRecord const& record) const
{
    return t <= record.t;
}
//----------------------------------------------------------------------------
inline bool PickRecord::operator>(PickRecord const& record) const
{
    return t > record.t;
}
//----------------------------------------------------------------------------
inline bool PickRecord::operator>=(PickRecord const& record) const
{
    return t >= record.t;
}
//----------------------------------------------------------------------------

}
