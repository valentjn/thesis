// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.0 (2014/08/11)

#pragma once

#include <gte/GteDX11Include.h>
#include <gte/GTEngineDEF.h>
#include <vector>

namespace gte
{

class GTE_IMPEXP HLSLDefiner
{
public:
    // Construction.
    HLSLDefiner();

    // Construct defines (preprocessor symbols in the HLSL file).
    HLSLDefiner& SetInt(std::string const& name, int value);
    HLSLDefiner& SetUnsignedInt(std::string const& name, unsigned int value);
    HLSLDefiner& SetFloat(std::string const& name, float value);
    HLSLDefiner& SetDouble(std::string const& name, double value);
    HLSLDefiner& SetString(std::string const& name, std::string const& value);

    // The returned pointer is valid only until a call is made to one of the
    // Set* functions.
    D3D_SHADER_MACRO const* GetMacros() const;

    // Clear out the macros, which allows sharing of an HLSLDefiner object
    // within a scope.
    void Clear();

private:
    // Maintain an array of string names and values.
    enum class GTE_IMPEXP DefineType
    {
        DT_INT,
        DT_UNSIGNED_INT,
        DT_FLOAT,
        DT_DOUBLE,
        DT_STRING
    };

    struct GTE_IMPEXP Define
    {
        DefineType type;
        std::string name;
        std::string value;
    };

    std::vector<Define> mDefines;

    HLSLDefiner& Set(DefineType type, std::string const& name,
        std::string const& value);

    // DirectX expects an array of D3D_SHADER_MACRO objects that store
    // 'const char*' pointers to names and values.  A call to GetMacros()
    // sets these pointers to the character data in the Define 'name's
    // and 'value's.  The mutable attribute is used so that GetMacros()
    // has conceptual constness.
    mutable std::vector<D3D_SHADER_MACRO> mMacros;
};

}
