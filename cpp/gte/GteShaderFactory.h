// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.5 (2015/02/19)

#pragma once

#include <gte/GteComputeShader.h>
#include <gte/GteGeometryShader.h>
#include <gte/GteHLSLFactory.h>
#include <gte/GtePixelShader.h>
#include <gte/GteVertexShader.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

#define GTE_DEFAULT_HLSL_COMPILE_FLAGS (D3DCOMPILE_ENABLE_STRICTNESS | D3DCOMPILE_IEEE_STRICTNESS | D3DCOMPILE_OPTIMIZATION_LEVEL3)

class GTE_IMPEXP ShaderFactory
{
public:
    static std::string defaultShaderModel;

    // Create a shader from an HLSL program in a file.
    static VertexShader* CreateVertex(
        std::string const& filename,
        HLSLDefiner const& definer = HLSLDefiner(),
        std::string const& entry = "VSMain",
        std::string const& target = std::string("vs_") + defaultShaderModel,
        unsigned int flags = GTE_DEFAULT_HLSL_COMPILE_FLAGS);

    static PixelShader* CreatePixel(
        std::string const& filename,
        HLSLDefiner const& definer = HLSLDefiner(),
        std::string const& entry = "PSMain",
        std::string const& target = std::string("ps_") + defaultShaderModel,
        unsigned int flags = GTE_DEFAULT_HLSL_COMPILE_FLAGS);

    static GeometryShader* CreateGeometry(
        std::string const& filename,
        HLSLDefiner const& definer = HLSLDefiner(),
        std::string const& entry = "GSMain",
        std::string const& target = std::string("gs_") + defaultShaderModel,
        unsigned int flags = GTE_DEFAULT_HLSL_COMPILE_FLAGS);

    static ComputeShader* CreateCompute(
        std::string const& filename,
        HLSLDefiner const& definer = HLSLDefiner(),
        std::string const& entry = "CSMain",
        std::string const& target = std::string("cs_") + defaultShaderModel,
        unsigned int flags = GTE_DEFAULT_HLSL_COMPILE_FLAGS);

    // Create a shader from an HLSL represented as a string.
    static VertexShader* CreateVertex(
        std::string const& name,
        std::string const& source,
        HLSLDefiner const& definer = HLSLDefiner(),
        std::string const& entry = "VSMain",
        std::string const& target = std::string("vs_") + defaultShaderModel,
        unsigned int flags = GTE_DEFAULT_HLSL_COMPILE_FLAGS);

    static PixelShader* CreatePixel(
        std::string const& name,
        std::string const& source,
        HLSLDefiner const& definer = HLSLDefiner(),
        std::string const& entry = "PSMain",
        std::string const& target = std::string("ps_") + defaultShaderModel,
        unsigned int flags = GTE_DEFAULT_HLSL_COMPILE_FLAGS);

    static GeometryShader* CreateGeometry(
        std::string const& name,
        std::string const& source,
        HLSLDefiner const& definer = HLSLDefiner(),
        std::string const& entry = "GSMain",
        std::string const& target = std::string("gs_") + defaultShaderModel,
        unsigned int flags = GTE_DEFAULT_HLSL_COMPILE_FLAGS);

    static ComputeShader* CreateCompute(
        std::string const& name,
        std::string const& source,
        HLSLDefiner const& definer = HLSLDefiner(),
        std::string const& entry = "CSMain",
        std::string const& target = std::string("cs_") + defaultShaderModel,
        unsigned int flags = GTE_DEFAULT_HLSL_COMPILE_FLAGS);

    // Create a shader from an HLSL represented as a bytecode blob.
    static VertexShader* CreateVertex(
        std::string const& name,
        size_t numBytes,
        unsigned char const* bytecode,
        std::string const& entry = "VSMain",
        std::string const& target = std::string("vs_") + defaultShaderModel);

    static PixelShader* CreatePixel(
        std::string const& name,
        size_t numBytes,
        unsigned char const* bytecode,
        std::string const& entry = "PSMain",
        std::string const& target = std::string("ps_") + defaultShaderModel);

    static GeometryShader* CreateGeometry(
        std::string const& name,
        size_t numBytes,
        unsigned char const* bytecode,
        std::string const& entry = "GSMain",
        std::string const& target = std::string("gs_") + defaultShaderModel);

    static ComputeShader* CreateCompute(
        std::string const& name,
        size_t numBytes,
        unsigned char const* bytecode,
        std::string const& entry = "CSMain",
        std::string const& target = std::string("cs_") + defaultShaderModel);

private:
    // Create a shader from an HLSL program in a file.
    static Shader* Create(
        std::string const& filename,
        HLSLDefiner const& definer,
        std::string const& entry,
        std::string const& target,
        unsigned int flags);

    // Create a shader from an HLSL represented as a string.
    static Shader* Create(
        std::string const& name,
        std::string const& source,
        HLSLDefiner const& definer,
        std::string const& entry,
        std::string const& target,
        unsigned int flags);

    // Create a shader from an HLSL bytecode blob.
    static Shader* Create(
        std::string const& name,
        std::string const& entry,
        std::string const& target,
        size_t numBytes,
        unsigned char const* bytecode);
};

}
