use bevy::prelude::*;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct UnitTest;

#[derive(Component, Reflect, Default, Debug, Deref, DerefMut)]
#[reflect(Component)]
struct TuppleTestF32(f32);

#[derive(Component, Reflect, Default, Debug, Deref, DerefMut)]
#[reflect(Component)]
struct TuppleTestU64(u64);

#[derive(Component, Reflect, Default, Debug, Deref, DerefMut)]
#[reflect(Component)]
pub struct TuppleTestStr(String);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TuppleTest2(f32, u64, String);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TuppleTestBool(bool);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TuppleVec2(Vec2);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TuppleVec3(Vec3);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TuppleVec(Vec<String>);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TuppleTestColor(Color);

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
            .register_type::<TuppleTestF32>()
            .register_type::<TuppleTestU64>()
            .register_type::<TuppleTestStr>()
            .register_type::<TuppleTestBool>()
            .register_type::<TuppleTest2>()
            .register_type::<TuppleVec2>()
            .register_type::<TuppleVec3>()
            .register_type::<EnumTest>()
            .register_type::<TuppleTestColor>()
            .register_type::<TuppleVec>()
            .register_type::<Vec<String>>();
    }
}
