#include <gazebo/gazebo.hh>
#include <gazebo/physics/physics.hh>
#include <ignition/math/Vector3.hh>
#include <ignition/math/Pose3.hh>
#include <gazebo/common/Time.hh>
#include <cmath>


namespace gazebo
{
class CircularMovePlugin : public ModelPlugin
{
public:
void Load(physics::ModelPtr _model, sdf::ElementPtr _sdf) override
{
model = _model;
world = model->GetWorld();


radius = _sdf->HasElement("radius") ? _sdf->Get<double>("radius") : 1.0;
angular_speed = _sdf->HasElement("angular_speed") ? _sdf->Get<double>("angular_speed") : 0.8; // rad/s


center = model->WorldPose();
center.Pos() = center.Pos(); // keep
angle = 0.0;
last_time = world->SimTime();


updateConnection = event::Events::ConnectWorldUpdateBegin(
std::bind(&CircularMovePlugin::OnUpdate, this));
}


void OnUpdate()
{
gazebo::common::Time now = world->SimTime();
double dt = (now - last_time).Double();
last_time = now;


angle += angular_speed * dt;
double nx = center.Pos().X() + radius * cos(angle);
double ny = center.Pos().Y() + radius * sin(angle);
double nz = center.Pos().Z();


ignition::math::Pose3d newPose(ignition::math::Vector3d(nx, ny, nz), ignition::math::Quaterniond(0,0,0));
model->SetWorldPose(newPose);
}


private:
physics::ModelPtr model;
physics::WorldPtr world;
event::ConnectionPtr updateConnection;
ignition::math::Pose3d center;
double radius{1.0};
double angular_speed{0.8};
double angle{0.0};
gazebo::common::Time last_time;
};


GZ_REGISTER_MODEL_PLUGIN(CircularMovePlugin)
}