// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.1 (2014/12/13)

#pragma once

#include <gte/GteCuller.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

// Support for a spatial hierarchy of objects.  Class Spatial has a parent
// pointer.  Class Node derives from Spatial has an array of child pointers.
// The leaf nodes of the hierarchy are either graphical or audial.  Class
// Visual derives from Spatial and represents graphical data.  Class Audial
// derives from Spatial and represents sound data.

class GTE_IMPEXP Spatial
{
public:
    // Abstract base class.
    virtual ~Spatial ();

    // Update of geometric state.  The function computes world transformations
    // on the downward pass of the scene graph traversal and world bounding
    // volumes on the upward pass of the traversal.  The object that calls the
    // update is the initiator.  Other objects visited during the update are
    // not initiators.
    void Update (bool initiator = true);

    // Access to the parent object, which is null for the root of the
    // hierarchy.
    inline Spatial* GetParent ();

    // Public member access.
    Transform<float> localTransform;
    Transform<float> worldTransform;
    BoundingSphere worldBound;
    CullingMode culling;

public:
    // Support for hierarchical culling.
    void OnGetVisibleSet (Culler& culler, bool noCull);
    virtual void GetVisibleSet (Culler& culler, bool noCull) = 0;

    // Access to the parent object.  Node calls this during attach/detach of
    // children.
    void SetParent (Spatial* parent);

protected:
    // Constructor accessible by Node, Visual, and Audial.
    Spatial ();

    // Support for geometric updates.
    virtual void UpdateWorldData ();
    virtual void UpdateWorldBound () = 0;
    void PropagateBoundToRoot ();

private:
    // Support for a hierarchical scene graph.  Spatial provides the parent
    // pointer.  Node provides the child pointers.  The parent pointer is not
    // shared to avoid cycles in the scene graph.  It is not necessary to use
    // std::weak_ptr here.
    Spatial* mParent;
};

//----------------------------------------------------------------------------
inline Spatial* Spatial::GetParent()
{
    return mParent;
}
//----------------------------------------------------------------------------
inline void Spatial::SetParent(Spatial* parent)
{
    mParent = parent;
}
//----------------------------------------------------------------------------

}
