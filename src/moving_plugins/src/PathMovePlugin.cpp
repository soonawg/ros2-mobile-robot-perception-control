#include <gazebo/gazebo.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo/common/Time.hh>
#include <ignition/math/Vector3.hh>
#include <vector>
#include <string>
#include <sstream>


namespace gazebo
{
class PathMovePlugin : public ModelPlugin
{
public:
void Load(physics::ModelPtr _model, sdf::ElementPtr _sdf) override
{
model = _model;
world = model->GetWorld();


// default waypoints string: "0 0; 1 0; 1 1; 0 1"
std::string wp_str = _sdf->HasElement("waypoints") ? _sdf->Get<std::string>("waypoints") : "";
speed = _sdf->HasElement("speed") ? _sdf->Get<double>("speed") : 0.4;


if (!wp_str.empty())
{
std::stringstream ss(wp_str);
std::string pair;
while (std::getline(ss, pair, ';'))
{
std::stringstream ps(pair);
double x,y;
if (ps >> x >> y)
{
waypoints.emplace_back(x,y);
}
}
}


if (waypoints.empty())
{
// fallback: simple square
waypoints.push_back({0,0});
waypoints.push_back({1,0});
waypoints.push_back({1,1});
waypoints.push_back({0,1});
}


current_idx = 0;
last_time = world->SimTime();
updateConnection = event::Events::ConnectWorldUpdateBegin(
std::bind(&PathMovePlugin::OnUpdate, this));
}


void OnUpdate()
{
gazebo::common::Time now = world->SimTime();
double dt = (now - last_time).Double();
last_time = now;


ignition::math::Vector3d pos = model->WorldPose().Pos();
auto target = waypoints[current_idx];
ignition::math::Vector3d tpos(target.first, target.second, pos.Z());


ignition::math::Vector3d diff = tpos - pos;
double dist = diff.Length();
if (dist < 0.05)
{
current_idx = (current_idx + 1) % waypoints.size();
return;
}


ignition::math::Vector3d direction = diff.Normalize();
ignition::math::Vector3d vel = direction * speed;
model->SetLinearVel(vel);
}


private:
physics::ModelPtr model;
physics::WorldPtr world;
event::ConnectionPtr updateConnection;
std::vector<std::pair<double,double>> waypoints;
size_t current_idx{0};
double speed{0.4};
gazebo::common::Time last_time;
};


GZ_REGISTER_MODEL_PLUGIN(PathMovePlugin)
}