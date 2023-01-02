/*
 * test_parser_speed.cc
 *
 *  Created on: Feb 2, 2020
 *      Author: jb
 */




/*
 * test_parser.cc
 *
 *  Created on: Jan 11, 2020
 *      Author: jb
 */

#include <string>
#include <chrono>
#include <cmath>
#include <iostream>
#include <fstream>

#include "assert.hh"
#include "parser.hh"
#include "test_tools.hh"

#include "arena_alloc.hh"

// Optimized structure, holds data in common arena
struct ExprData {
	ExprData(uint vec_size)
	: vec_size(vec_size)
	{

		arena = std::make_shared<bparser::ArenaAlloc>(32, 512 * 1012);
		v1 = arena->create_array<double>(vec_size * 3);
		fill_seq(v1, 100, 100 + 3 * vec_size);
		v2 = arena->create_array<double>(vec_size * 3);
		fill_seq(v2, 200, 200 + 3 * vec_size);
		v3 = arena->create_array<double>(vec_size * 3);
		fill_seq(v3, 300, 300 + 3 * vec_size);
		v4 = arena->create_array<double>(vec_size * 3);
		fill_seq(v4, 400, 400 + 3 * vec_size);
		vres = arena->create_array<double>(vec_size * 3);
		fill_const(vres, 3 * vec_size, -100);
		subset = arena->create_array<uint>(vec_size);
		for(uint i=0; i<vec_size/4; i++) subset[i] = i;
		cs1 = 4;
		for (uint i = 0; i < 3; i++)
		{
			cv1[i] = (i+1)*3;
		}
	}	

	~ExprData()
	{}

	std::shared_ptr<bparser::ArenaAlloc> arena;
	uint vec_size;
	uint simd_size;
	double *v1, *v2, *v3, *v4, *vres;
	double cs1;
	double cv1[3];
	uint *subset;

};





/**
 * @param expr       Parser expression
 * @param block_size Number of floats
 * @param i_expr     Specifies C++ expression function
 */
void test_expr(std::string expr, uint block_size, std::string expr_id, std::ofstream& file) {
	using namespace bparser;
	uint vec_size = 1*block_size;

	// uint simd_size = get_simd_size();

	// TODO: allow changing variable pointers, between evaluations
	// e.g. p.set_variable could return pointer to that pointer
	// not so easy for vector and tensor variables, there are many pointers to set
	// Rather modify the test to fill the
	uint n_repeats = (1024 / block_size) * 100000;

	ExprData  data1(vec_size);

	// double parser_time_optim, parser_time_shared_arena, parser_time_copy, parser_time_noopt, cpp_time;
	double parser_time_shared_arena;

	// { // one allocation in common arena
	// 	Parser p(block_size);
	// 	p.parse(expr);
	// 	p.set_constant("cs1", {}, 	{data1.cs1});
	// 	p.set_constant("cv1", {3}, 	std::vector<double>(data1.cv1, data1.cv1+3));
	// 	p.set_variable("v1", {3}, data1.v1);
	// 	p.set_variable("v2", {3}, data1.v2);
	// 	p.set_variable("v3", {3}, data1.v3);
	// 	p.set_variable("v4", {3}, data1.v4);
	// 	p.set_variable("_result_", {3}, data1.vres);
	// 	//std::cout << "vres: " << vres << ", " << vres + block_size << ", " << vres + 2*vec_size << "\n";
	// 	//std::cout << "Symbols: " << print_vector(p.symbols()) << "\n";
	// 	//std::cout.flush();
	// 	p.compile();

	// 	std::vector<uint> ss = std::vector<uint>(data1.subset, data1.subset+vec_size/simd_size);
	// 	p.set_subset(ss);
	// 	auto start_time = std::chrono::high_resolution_clock::now();
	// 	for(uint i_rep=0; i_rep < n_repeats; i_rep++) {
	// 		p.run();
	// 	}
	// 	auto end_time = std::chrono::high_resolution_clock::now();
	// 	parser_time_optim = std::chrono::duration_cast<std::chrono::duration<double>>(end_time - start_time).count();
	// }

	{ // one allocation in common arena, set this arena to processor
		Parser p(block_size);
		p.parse(expr);
		p.set_constant("cs1", {}, 	{data1.cs1});
		p.set_constant("cv1", {3}, 	std::vector<double>(data1.cv1, data1.cv1+3));
		p.set_variable("v1", {3}, data1.v1);
		p.set_variable("v2", {3}, data1.v2);
		p.set_variable("v3", {3}, data1.v3);
		p.set_variable("v4", {3}, data1.v4);
		p.set_variable("_result_", {3}, data1.vres);
		//std::cout << "vres: " << vres << ", " << vres + block_size << ", " << vres + 2*vec_size << "\n";
		//std::cout << "Symbols: " << print_vector(p.symbols()) << "\n";
		//std::cout.flush();
		p.compile(data1.arena);

		std::vector<uint> ss = std::vector<uint>(data1.subset, data1.subset+vec_size/4);
		p.set_subset(ss);
		auto start_time = std::chrono::high_resolution_clock::now();
		for(uint i_rep=0; i_rep < n_repeats; i_rep++) {
			p.run();
		}
		auto end_time = std::chrono::high_resolution_clock::now();
		parser_time_shared_arena = std::chrono::duration_cast<std::chrono::duration<double>>(end_time - start_time).count();
	}

	// { // one allocation in common arena, use set_var_copy
	// 	Parser p(block_size);
	// 	p.parse(expr);
	// 	p.set_constant("cs1", {}, 	{data4.cs1});
	// 	p.set_constant("cv1", {3}, 	std::vector<double>(data4.cv1, data4.cv1+3));
	// 	p.set_var_copy("v1", {3}, data4.v1);
	// 	p.set_var_copy("v2", {3}, data4.v2);
	// 	p.set_var_copy("v3", {3}, data4.v3);
	// 	p.set_var_copy("v4", {3}, data4.v4);
	// 	p.set_variable("_result_", {3}, data4.vres);
	// 	//std::cout << "vres: " << vres << ", " << vres + block_size << ", " << vres + 2*vec_size << "\n";
	// 	//std::cout << "Symbols: " << print_vector(p.symbols()) << "\n";
	// 	//std::cout.flush();
	// 	p.compile();

	// 	std::vector<uint> ss = std::vector<uint>(data4.subset, data4.subset+vec_size/simd_size);
	// 	p.set_subset(ss);
	// 	auto start_time = std::chrono::high_resolution_clock::now();
	// 	for(uint i_rep=0; i_rep < n_repeats; i_rep++) {
	// 		p.run();
	// 	}
	// 	auto end_time = std::chrono::high_resolution_clock::now();
	// 	parser_time_copy = std::chrono::duration_cast<std::chrono::duration<double>>(end_time - start_time).count();
	// }

	// { // unoptimized allocation in separated arenas
	// 	Parser p(block_size);
	// 	p.parse(expr);
	// 	p.set_constant("cs1", {}, 	{data2.cs1});
	// 	p.set_constant("cv1", {3}, 	std::vector<double>(data2.cv1, data2.cv1+3));
	// 	p.set_variable("v1", {3}, data2.v1);
	// 	p.set_variable("v2", {3}, data2.v2);
	// 	p.set_variable("v3", {3}, data2.v3);
	// 	p.set_variable("v4", {3}, data2.v4);
	// 	p.set_variable("_result_", {3}, data2.vres);
	// 	//std::cout << "vres: " << vres << ", " << vres + block_size << ", " << vres + 2*vec_size << "\n";
	// 	//std::cout << "Symbols: " << print_vector(p.symbols()) << "\n";
	// 	//std::cout.flush();
	// 	p.compile();

	// 	std::vector<uint> ss = std::vector<uint>(data2.subset, data2.subset+vec_size/simd_size);
	// 	p.set_subset(ss);
	// 	auto start_time = std::chrono::high_resolution_clock::now();
	// 	for(uint i_rep=0; i_rep < n_repeats; i_rep++) {
	// 		data2.copy_to_arena();
	// 		p.run();
	// 		data2.copy_from_arena();
	// 	}
	// 	auto end_time = std::chrono::high_resolution_clock::now();
	// 	parser_time_noopt = std::chrono::duration_cast<std::chrono::duration<double>>(end_time - start_time).count();
	// }


	// check
	double p_sum = 0;
	for(uint dim=0; dim < 3; dim++) {
		for(uint i=0; i<data1.vec_size; i++) {
			double v1 = data1.vres[dim*data1.vec_size + i];
			//std::cout << "res: " << v1 <<std::endl;
			p_sum += v1;
		}
	}
	double n_flop = n_repeats * vec_size * 9;

	// std::cout << "=== Parsing of expression: '" << expr << "' ===\n";
	// std::cout << "Result	  : " << p_sum << "\n";
	// std::cout << "Block size: " << block_size << "\n";
	// std::cout << "Experession id: " << expr_id << "\n";
	// // std::cout << "Diff: " << diff << " parser: " << p_sum << " c++: " << c_sum << "\n";
	// // std::cout << "parser time optim   : " << parser_time_optim << "\n";
	// std::cout << "Parser time : " << parser_time_shared_arena << "\n";
	// // std::cout << "parser time copy    : " << parser_time_copy << "\n";
	// // std::cout << "parser time noopt   : " << parser_time_noopt << "\n";
	// // std::cout << "c++ time            : " << cpp_time << "\n";
	// // std::cout << "fraction: " << parser_time_optim/cpp_time << "\n";
	// std::cout << "Parser FLOPS: " << n_flop / parser_time_shared_arena << "\n";
	// // std::cout << "c++ FLOPS   : " << n_flop / cpp_time << "\n";
	// std::cout << "======================================================\n\n";

	file << "BParser_OLD;"<< expr_id << ";"<< expr << ";"<< p_sum << ";"<< n_repeats << ";"<< block_size << ";" << parser_time_shared_arena << ";" << parser_time_shared_arena/n_repeats/vec_size*1e9 << ";" << n_flop/parser_time_shared_arena << "\n";

}




void test_expression(std::string filename)  {
	std::vector<uint> block_sizes = {64, 256, 1024};

	std::ofstream file;
	if(!filename.empty())
	{
		file.open(filename);
		std::cout << "Outputing to " << filename << "\n";
	}
	else
	{
		file.open("BParser_vystup.csv");
	}

	//header
	file << "Executor;ID;Expression;Result;Repeats;BlockSize;Time;Avg. time per single execution;FLOPS\n";

	for (uint i=0; i<block_sizes.size(); ++i) {
		uint id_counter = 0;
		test_expr("-v1", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("v1 + v2", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("v1 - v2", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("v1 * v2", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("v1 / v2", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("v1 % v2", block_sizes[i], std::to_string(id_counter++), file);

		test_expr("(v1 == v2)", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("v1 != v2", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("v1 < v2", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("v1 <= v2", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("v1 > v2", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("v1 >= v2", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("not (v1 == v2)", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("v1 or v2", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("v1 and v2", block_sizes[i], std::to_string(id_counter++), file);

		test_expr("abs(v1)", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("sqrt(v1)", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("exp(v1)", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("log(v1)", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("log10(v1)", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("sin(v1)", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("sinh(v1)", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("asin(v1)", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("cos(v1)", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("cosh(v1)", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("acos(v1)", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("tan(v1)", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("tanh(v1)", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("atan(v1)", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("ceil(v1)", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("floor(v1)", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("isnan(v1)", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("isinf(v1)", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("sgn(v1)", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("atan2(v1, v2)", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("v1 ** v2", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("maximum(v1, v2)", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("minimum(v1, v2)", block_sizes[i], std::to_string(id_counter++), file);

		test_expr("v3 if v1 == v2 else v4", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("cv1 + v1 + v2 - v3", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("cs1 - v1 + v2 * v3", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("cs1 * v1 / v2", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("cv1 / v1 * v2 / v3", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("v1 + v2 + v3 + v4", block_sizes[i], std::to_string(id_counter++), file);
		test_expr("3 * v1 + cs1 * v2 + v3 + 2.5 * v4", block_sizes[i], std::to_string(id_counter++), file);
		// test_expr("[v2, v2, v2] @ v1 + v3", block_sizes[i], std::to_string(id_counter++), file);
	}
}



int main(int argc, char * argv[])
{
	std::string soubor = "";
	if(argc > 1)
	{
		soubor = argv[1]; 
	}
	test_expression(soubor);
}




