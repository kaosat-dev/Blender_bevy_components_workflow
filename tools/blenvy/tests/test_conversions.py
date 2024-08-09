from ..bevy_components.propGroups.conversions_to_prop_group import parse_struct_string, parse_tuplestruct_string


def test_parse_tuplestruct_string():
    assert parse_tuplestruct_string("(A)", start_nesting=1) == ['A']
    assert parse_tuplestruct_string("[(A)]", start_nesting=1) == ['(A)']

    assert parse_tuplestruct_string("(a: 45, b: 65)", start_nesting=1) == ['a: 45', 'b: 65']
    assert parse_tuplestruct_string("[(a: 45, b: 65)]", start_nesting=1) == ['(a: 45, b: 65)']
    assert parse_tuplestruct_string("45, 65, 'bla'", start_nesting=0) == ['45', '65', "'bla'"]

    assert parse_tuplestruct_string("[(A), (B)]", start_nesting=1) == ['(A)', '(B)']

    assert parse_tuplestruct_string("([(-1.8, 2.9), (0.0, -62)])", start_nesting=1) == ['[(-1.8, 2.9), (0.0, -62)]']
    assert parse_tuplestruct_string("([(-1.8, 2.9), (0.0, -62)])", start_nesting=2) == ['(-1.8, 2.9)', '(0.0, -62)']
    assert parse_tuplestruct_string("([(-1.8, 2.9), (0.0, -62), (25)])", start_nesting=2) == ['(-1.8, 2.9)', '(0.0, -62)', '(25)']

    assert parse_tuplestruct_string("(Vec3(x:-2.0, y:120.0, z:1.0))", start_nesting=2) == ['x:-2.0', 'y:120.0', 'z:1.0']

    assert parse_tuplestruct_string("(9)", start_nesting=1) == ['9']
    assert parse_tuplestruct_string('("toto")', start_nesting=1) == ['"toto"']
    
    assert parse_tuplestruct_string("(Rgba(red:0.0, green:0.2, blue:0.9, alpha:1.0))", start_nesting=1) == ['Rgba(red:0.0, green:0.2, blue:0.9, alpha:1.0)']
    assert parse_tuplestruct_string("(Rgba(red:0.0, green:0.2, blue:0.9, alpha:1.0))", start_nesting=2) == ['red:0.0', 'green:0.2', 'blue:0.9', 'alpha:1.0']

    assert parse_tuplestruct_string("([(-1.2, 2.9), (0.0, -62)])", start_nesting=2) == ['(-1.2, 2.9)', '(0.0, -62)']

    assert parse_tuplestruct_string("([Rgba(red:1.0, green:1.0, blue:0.0, alpha:1.0), Rgba(red:1.0, green:0.0, blue:0.5, alpha:1.0)])", start_nesting=2) == ['Rgba(red:1.0, green:1.0, blue:0.0, alpha:1.0)', 'Rgba(red:1.0, green:0.0, blue:0.5, alpha:1.0)']
    assert parse_tuplestruct_string('(7.2, 2607, "sdf")', start_nesting=1) == ['7.2', '2607', '"sdf"']

    assert parse_tuplestruct_string('[a, b]', start_nesting=1) == ['a', 'b']
    assert parse_tuplestruct_string('[]', start_nesting=1) == []

def test_parse_struct_string():
    assert parse_struct_string("a: 45, b:65") == {'a': '45', 'b':'65'}
    assert parse_struct_string("x:-2.0, y:120.0, z:1.0") == {'x': '-2.0', 'y':'120.0', 'z':'1.0'}

    assert parse_struct_string("enabled: true") == {'enabled': 'true'}
    assert parse_struct_string("(enabled: true)", start_nesting=1) == {'enabled': 'true'}


    assert parse_struct_string("(filters: (25), memberships: (5))", start_nesting=1) == {'filters': '(25)', 'memberships':'(5)'}
    assert parse_struct_string("groups: 0", start_nesting=0) == {'groups': '0'}
    assert parse_struct_string("(groups: 0)", start_nesting=1) == {'groups': '0'}

    assert parse_struct_string("(composite_mode: EnergyConserving, high_pass_frequency: 4.0, intensity: 0.0, low_frequency_boost: -6.0, low_frequency_boost_curvature: 4.1, prefilter_settings: (threshold: -5.1, threshold_softness: 2.1))", start_nesting=1) == {'composite_mode': 'EnergyConserving', 'high_pass_frequency': '4.0', 'intensity': '0.0', 'low_frequency_boost': '-6.0', 'low_frequency_boost_curvature': '4.1', 'prefilter_settings': '(threshold: -5.1, threshold_softness: 2.1)'}

    
    assert parse_struct_string("dimensions: UVec3(x:0.0, y:0.0, z:0.0), dynamic_resizing: true, z_config: (far_z_mode: MaxLightRange, first_slice_depth: 0.0)") == {'dimensions': 'UVec3(x:0.0, y:0.0, z:0.0)', 'dynamic_resizing': 'true', 'z_config': '(far_z_mode: MaxLightRange, first_slice_depth: 0.0)'}

    assert parse_struct_string('(inverse_bindposes: Strong(""), joints: [4294967295, 4294967295, 4294967295])', start_nesting=1) == {'inverse_bindposes': 'Strong("")', 'joints': '[4294967295, 4294967295, 4294967295]'}