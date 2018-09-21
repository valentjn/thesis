// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.0 (2014/08/11)

#pragma once

#include <gte/GteComputeShader.h>
#include <gte/GteDX11Engine.h>
#include <gte/GteFluid2Parameters.h>
#include <gte/GteTexture2.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

class GTE_IMPEXP Fluid2InitializeSource
{
public:
    // Construction and destruction.  The source density consists of a
    // density producer (increase density) and a density consumer (decrease
    // density).  Each has a location, a variance from that location, and
    // an amplitude.  The source velocity (impulse) is generated from gravity,
    // a single wind source, and randomly generated vortices.  Each vortex is
    // selected with a random location, a variance from that location, and an
    // amplitude for the impulse.
    ~Fluid2InitializeSource();
    Fluid2InitializeSource(int xSize, int ySize, int numXThreads,
        int numYThreads,
        std::shared_ptr<gte::ConstantBuffer> const& parameters);

    // Member access.  The texels are (velocity.x, velocity.y, 0, density).
    // The third component is unused in the simulation (a 3D simulation will
    // store velocity.z in this component).
    std::shared_ptr<gte::Texture2> const& GetSource() const;

    // Compute the source density and source velocity for the fluid
    // simulation.
    void Execute(gte::DX11Engine* engine);

private:
    enum { NUM_VORTICES = 1024 };

    struct Vortex
    {
        gte::Vector4<float> data;
    };

    struct External
    {
        gte::Vector4<float> densityProducer;
        gte::Vector4<float> densityConsumer;
        gte::Vector4<float> gravity;
        gte::Vector4<float> wind;
    };

    int mNumXGroups, mNumYGroups;
    std::shared_ptr<gte::ComputeShader> mGenerateVortex;
    std::shared_ptr<gte::ComputeShader> mInitializeSource;
    std::shared_ptr<gte::ConstantBuffer> mVortex;
    std::shared_ptr<gte::ConstantBuffer> mExternal;
    std::shared_ptr<gte::Texture2> mVelocity0;
    std::shared_ptr<gte::Texture2> mVelocity1;
    std::shared_ptr<gte::Texture2> mSource;

    static std::string const msHLSLGenerateVortexString;
    static std::string const msHLSLInitializeSourceString;
};

}
