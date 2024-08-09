use bevy::prelude::*;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct UnitTest;

#[derive(Component, Reflect, Default, Debug, Deref, DerefMut)]
#[reflect(Component)]
struct TupleTestF32(f32);

#[derive(Component, Reflect, Default, Debug, Deref, DerefMut)]
#[reflect(Component)]
struct TupleTestU64(u64);

#[derive(Component, Reflect, Default, Debug, Deref, DerefMut)]
#[reflect(Component)]
pub struct TupleTestStr(String);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TupleTest2(f32, u64, String);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TupleTestBool(bool);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TupleVec2(Vec2);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TupleVec3(Vec3);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TupleVec(Vec<String>);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TupleTestColor(Color);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct BasicTest {
    a: f32,
    b: u64,
    c: String,
}

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub enum EnumTest {
    Metal,
    Wood,
    Rock,
    Cloth,
    Squishy,
    #[default]
    None,
}

pub struct ComponentsTestPlugin;
impl Plugin for ComponentsTestPlugin {
    fn build(&self, app: &mut App) {
        app.register_type::<BasicTest>()
            .register_type::<UnitTest>()
            .register_type::<TupleTestF32>()
            .register_type::<TupleTestU64>()
            .register_type::<TupleTestStr>()
            .register_type::<TupleTestBool>()
            .register_type::<TupleTest2>()
            .register_type::<TupleVec2>()
            .register_type::<TupleVec3>()
            .register_type::<EnumTest>()
            .register_type::<TupleTestColor>()
            .register_type::<TupleVec>()
            .register_type::<Vec<String>>();
    }
}
