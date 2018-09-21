// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.0 (2014/08/11)

#pragma once

#include <gte/GteHLSLResource.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

class GTE_IMPEXP HLSLStructuredBuffer : public HLSLResource
{
public:
    enum GTE_IMPEXP Type
    {
        SBT_INVALID,
        SBT_BASIC,
        SBT_APPEND,
        SBT_CONSUME,
        SBT_COUNTER
    };

    // Construction and destruction.
    virtual ~HLSLStructuredBuffer();

    HLSLStructuredBuffer(D3D11_SHADER_INPUT_BIND_DESC const& desc);

    HLSLStructuredBuffer(D3D11_SHADER_INPUT_BIND_DESC const& desc,
        unsigned int index);

    // Member access.
    Type GetType() const;
    bool IsGpuWritable() const;

private:
    void Initialize(D3D11_SHADER_INPUT_BIND_DESC const& desc);

    Type mType;
    bool mGpuWritable;
};

}
