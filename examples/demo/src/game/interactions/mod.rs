#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// Demo marker component
pub struct Interactible;

pub struct InteractionsPlugin;
impl Plugin for InteractionsPlugin {
    fn build(&self, app: &mut App) {
        app.register_type::<Interactible>();
    }
}
