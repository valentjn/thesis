// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.0 (2014/08/11)

#pragma once

#include <gte/GteComputeShader.h>
#include <gte/GteDX11Engine.h>
#include <gte/GteFluid3Parameters.h>
#include <gte/GteTexture3.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

class GTE_IMPEXP Fluid3InitializeSource
{
public:
    // Construction and destruction.  The source density consists of a
    // density producer (increase density) and a density consumer (decrease
    // density).  Each has a location, a variance from that location, and
    // an amplitude.  The source velocity (impulse) is generated from gravity,
    // a single wind source, and randomly generated vortices.  Each vortex is
    // selected with a random location, a variance from that location, and an
    // amplitude for the impulse.
    ~Fluid3InitializeSource();
    Fluid3InitializeSource(int xSize, int ySize, int zSize, int numXThreads,
        int numYThreads, int numZThreads,
        std::shared_ptr<gte::ConstantBuffer> const& parameters);

    // Member access.  The texels are (velocity.xyz, density).
    std::shared_ptr<gte::Texture3> const& GetSource() const;

    // Compute the source density and source velocity for the fluid
    // simulation.
    void Execute(gte::DX11Engine* engine);

private:
    enum { NUM_VORTICES = 1024 };

    struct Vortex
    {
        gte::Vector4<float> position;
        gte::Vector4<float> normal;
        gte::Vector4<float> data;
    };

    struct External
    {
        gte::Vector4<float> densityProducer;  // (x, y, z, *)
        gte::Vector4<float> densityPData;     // (variance, amplitude, *, *)
        gte::Vector4<float> densityConsumer;  // (x, y, z, *)
        gte::Vector4<float> densityCData;     // (variance, amplitude, *, *)
        gte::Vector4<float> gravity;
        gte::Vector4<float> windData;
    };

    int mNumXGroups, mNumYGroups, mNumZGroups;
    std::shared_ptr<gte::ComputeShader> mGenerateVortex;
    std::shared_ptr<gte::ComputeShader> mInitializeSource;
    std::shared_ptr<gte::ConstantBuffer> mVortex;
    std::shared_ptr<gte::ConstantBuffer> mExternal;
    std::shared_ptr<gte::Texture3> mVelocity0;
    std::shared_ptr<gte::Texture3> mVelocity1;
    std::shared_ptr<gte::Texture3> mSource;

    static std::string const msHLSLGenerateVortexString;
    static std::string const msHLSLInitializeSourceString;
};

}
