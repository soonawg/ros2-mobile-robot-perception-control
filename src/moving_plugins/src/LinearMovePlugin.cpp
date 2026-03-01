#include <gazebo/gazebo.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo/common/Time.hh>
#include <ignition/math/Vector3.hh>
#include <string>


namespace gazebo
{
class LinearMovePlugin : public ModelPlugin
{
public:
LinearMovePlugin() : ModelPlugin() {}


void Load(physics::ModelPtr _model, sdf::ElementPtr _sdf) override
{
model = _model;
world = model->GetWorld();


// params
min_y = _sdf->HasElement("min_y") ? _sdf->Get<double>("min_y") : -1.0;
max_y = _sdf->HasElement("max_y") ? _sdf->Get<double>("max_y") : 1.0;


speed = _sdf->HasElement("velocity") ? _sdf->Get<double>("velocity") : 0.3;


// start direction positive
if (model->WorldPose().Pos().Y() > max_y) speed = -fabs(speed);


last_time = world->SimTime();
updateConnection = event::Events::ConnectWorldUpdateBegin(
std::bind(&LinearMovePlugin::OnUpdate, this));
}


void OnUpdate()
{
  ignition::math::Pose3d pose = model->WorldPose();
  double y = pose.Pos().Y();

  if (y >= max_y) speed = -fabs(speed);
  if (y <= min_y) speed = fabs(speed);

  // set linear velocity along Y
  model->SetLinearVel(ignition::math::Vector3d(0, speed, 0));
}


private:
physics::ModelPtr model;
physics::WorldPtr world;
event::ConnectionPtr updateConnection;
double min_y{ -1.0 };
double max_y{ 1.0 };
double speed{ 0.3 };
gazebo::common::Time last_time;
};


GZ_REGISTER_MODEL_PLUGIN(LinearMovePlugin)
}