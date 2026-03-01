#include <gazebo/gazebo.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo/common/Time.hh>
#include <ignition/math/Vector3.hh>
#include <random>


namespace gazebo
{
class RandomMovePlugin : public ModelPlugin
{
public:
void Load(physics::ModelPtr _model, sdf::ElementPtr _sdf) override
{
model = _model;
world = model->GetWorld();


max_speed = _sdf->HasElement("max_speed") ? _sdf->Get<double>("max_speed") : 0.6;
change_interval = _sdf->HasElement("change_interval") ? _sdf->Get<double>("change_interval") : 1.0;


rng.seed(std::random_device{}());
uni = std::uniform_real_distribution<double>(-1.0, 1.0);


time_acc = 0.0;
last_time = world->SimTime();
current_vel = ignition::math::Vector3d(0,0,0);


updateConnection = event::Events::ConnectWorldUpdateBegin(
std::bind(&RandomMovePlugin::OnUpdate, this));
}


void OnUpdate()
{
gazebo::common::Time now = world->SimTime();
double dt = (now - last_time).Double();
last_time = now;


time_acc += dt;
if (time_acc >= change_interval)
{
time_acc = 0.0;
double vx = uni(rng) * max_speed;
double vy = uni(rng) * max_speed;
current_vel = ignition::math::Vector3d(vx, vy, 0);
}


model->SetLinearVel(current_vel);
}


private:
physics::ModelPtr model;
physics::WorldPtr world;
event::ConnectionPtr updateConnection;
double max_speed{0.6};
double change_interval{1.0};
double time_acc{0.0};
gazebo::common::Time last_time;
ignition::math::Vector3d current_vel;
std::mt19937 rng;
std::uniform_real_distribution<double> uni;
};


GZ_REGISTER_MODEL_PLUGIN(RandomMovePlugin)
}