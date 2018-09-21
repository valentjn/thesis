// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.2.0 (2014/08/26)

#pragma once

#include <gte/GteMatrix4x4.h>

// The LightingConstants structure is shared among the classes
// LightAmbient, LightDirectionPerVertex, LightDirectionPerPixel,
// LightPointPerVertex, LightPointPerPixel, LightSpotPerVertex, and
// LightSpotPerPixel.  The structure is organized to match the default
// HLSL packing.  The '*' components are not used.  Not all members are
// used by a particular light type.  The individual header files have
// comments about which members are used.

namespace gte
{

struct GTE_IMPEXP LightingConstants
{
    // Construction.  The defaults are listed for each member.
    LightingConstants();

    // (r,g,b,*): default (0,0,0,1)
    Vector4<float> materialEmissive;

    // (r,g,b,*): default (0,0,0,1)
    Vector4<float> materialAmbient;

    // (r,g,b,a): default (0,0,0,1)
    Vector4<float> materialDiffuse;

    // (r,g,b,specularPower): default (0,0,0,1)
    Vector4<float> materialSpecular; 

    // (r,g,b,*): default (1,1,1,1)
    Vector4<float> lightAmbient;

    // (r,g,b,*): default (1,1,1,1)
    Vector4<float> lightDiffuse;

    // (r,g,b,*): default (1,1,1,1)
    Vector4<float> lightSpecular;

    // (angle,cosAngle,sinAngle,exp): default (pi/2,0,1,1)
    Vector4<float> lightSpotCutoff;

    // (*,*,*,w): default (1,0,0,1)
    Vector4<float> lightAttenuation;

    // (x,y,z,1): default (0,0,0,1)
    Vector4<float> cameraModelPosition;

    // (x,y,z,1): default (0,0,0,1)
    Vector4<float> lightModelPosition;

    // (x,y,z,0): default (0,0,0,0)
    Vector4<float> lightModelDirection;

    // model-to-world, rotation and translation only: default identity
    Matrix4x4<float> wMatrix;
};

}
