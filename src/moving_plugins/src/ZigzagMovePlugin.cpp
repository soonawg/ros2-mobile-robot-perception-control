#include <gazebo/gazebo.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo/common/Time.hh>
#include <ignition/math/Vector3.hh>
#include <cmath>


namespace gazebo
{
class ZigzagMovePlugin : public ModelPlugin
{
public:
void Load(physics::ModelPtr _model, sdf::ElementPtr _sdf) override
{
model = _model;
world = model->GetWorld();


forward_speed = _sdf->HasElement("forward_speed") ? _sdf->Get<double>("forward_speed") : 0.4;
lateral_speed = _sdf->HasElement("lateral_speed") ? _sdf->Get<double>("lateral_speed") : 0.6;
period = _sdf->HasElement("period") ? _sdf->Get<double>("period") : 1.5; // seconds


time_acc = 0.0;
last_time = world->SimTime();


updateConnection = event::Events::ConnectWorldUpdateBegin(
std::bind(&ZigzagMovePlugin::OnUpdate, this));
}


void OnUpdate()
{
gazebo::common::Time now = world->SimTime();
double dt = (now - last_time).Double();
last_time = now;


time_acc += dt;
// lateral direction alternates as square wave
double phase = fmod(time_acc / period, 2.0);
double lat = (phase < 1.0) ? lateral_speed : -lateral_speed;


// set velocity in local frame: forward in X, lateral in Y
ignition::math::Vector3d vel(forward_speed, lat, 0);
model->SetLinearVel(vel);
}


private:
physics::ModelPtr model;
physics::WorldPtr world;
event::ConnectionPtr updateConnection;
double forward_speed{0.4};
double lateral_speed{0.6};
double period{1.5};
double time_acc{0.0};
gazebo::common::Time last_time;
};


GZ_REGISTER_MODEL_PLUGIN(ZigzagMovePlugin)
}